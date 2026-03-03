from pathlib import Path

from main import remove_background_from_bytes

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def main() -> int:
    in_path = Path("test.jpg")
    out_path = Path("out.png")

    image_bytes = in_path.read_bytes()
    output_bytes = remove_background_from_bytes(image_bytes)
    out_path.write_bytes(output_bytes)

    sig_ok = output_bytes[:8] == PNG_SIG
    print(f"INPUT_BYTES={len(image_bytes)}")
    print(f"OUTPUT_BYTES={len(output_bytes)}")
    print(f"PNG_SIGNATURE_HEX={output_bytes[:8].hex().upper()}")
    print(f"PNG_SIGNATURE_OK={sig_ok}")
    return 0 if sig_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
