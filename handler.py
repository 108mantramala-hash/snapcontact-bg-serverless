import os
import io
import time
import uuid
import base64
import runpod
from PIL import Image

from main import remove_background_from_bytes

MAX_INPUT_BYTES = int(os.getenv("MAX_INPUT_BYTES", str(5 * 1024 * 1024)))   # 5MB
MAX_PIXELS      = int(os.getenv("MAX_PIXELS", str(4000 * 4000)))            # 16MP
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "25"))
RETURN_META     = os.getenv("RETURN_META", "1") == "1"
APP_KEY         = os.getenv("APP_KEY", "")


def _b64_to_bytes(b64_str: str) -> bytes:
    b64_str = "".join(b64_str.split())
    if len(b64_str) < 32:
        raise ValueError("image_base64 too short")

    try:
        raw = base64.b64decode(b64_str, validate=True)
    except Exception:
        raw = base64.b64decode(b64_str + "===")

    if not raw:
        raise ValueError("decoded bytes empty")

    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"image too large: {len(raw)} bytes (max {MAX_INPUT_BYTES})")

    return raw


def _validate_image(img_bytes: bytes) -> dict:
    try:
        im = Image.open(io.BytesIO(img_bytes))
        im.verify()
    except Exception:
        raise ValueError("input is not a valid image")

    im = Image.open(io.BytesIO(img_bytes))
    w, h = im.size
    pixels = w * h
    if pixels > MAX_PIXELS:
        raise ValueError(f"resolution too large: {w}x{h} ({pixels} px), max {MAX_PIXELS}")

    return {"width": w, "height": h, "format": (im.format or "unknown"), "mode": (im.mode or "unknown")}


def handler(job):
    request_id = str(uuid.uuid4())
    start = time.time()

    inp = job.get("input") or {}
    client_key = inp.get("app_key")
    if APP_KEY and client_key != APP_KEY:
        return {"ok": False, "request_id": request_id, "error": "Unauthorized"}

    img_b64 = inp.get("image_base64")
    if not img_b64:
        return {"ok": False, "request_id": request_id, "error": "Missing input.image_base64"}

    try:
        img_bytes = _b64_to_bytes(img_b64)
        meta_in = _validate_image(img_bytes)

        # Soft timeout guard
        if (time.time() - start) > TIMEOUT_SECONDS:
            return {"ok": False, "request_id": request_id, "error": "timeout before processing"}

        out_bytes = remove_background_from_bytes(img_bytes)

        if not out_bytes or len(out_bytes) < 32:
            return {"ok": False, "request_id": request_id, "error": "empty output from remover"}

        out_b64 = base64.b64encode(out_bytes).decode("utf-8")

        resp = {"ok": True, "request_id": request_id, "output_base64": out_b64}

        if RETURN_META:
            resp["meta"] = {
                "input": meta_in,
                "output_bytes": len(out_bytes),
                "elapsed_ms": int((time.time() - start) * 1000),
            }

        return resp

    except Exception as e:
        resp = {"ok": False, "request_id": request_id, "error": str(e)}
        if RETURN_META:
            resp["meta"] = {"elapsed_ms": int((time.time() - start) * 1000)}
        return resp


runpod.serverless.start({"handler": handler})
