from rembg import remove

def remove_background_from_bytes(image_bytes: bytes) -> bytes:
    return remove(image_bytes)  # returns PNG bytes w/ alpha