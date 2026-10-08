import io
import cv2
import numpy as np
from PIL import Image, ImageOps

MAX_SIDE = 1800


def preprocess(data: bytes) -> dict:
    """Decode, fix rotation, resize, clean. Raises ValueError for bad images."""
    try:
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img).convert("RGB")
    except Exception:
        raise ValueError("The file is not a valid image.")
    w, h = img.size
    if w < 20 or h < 20:
        raise ValueError("Image is too small.")
    scale = MAX_SIDE / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    original_jpeg = buf.getvalue()

    rgb = np.array(img)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 15)
    ok, png = cv2.imencode(".png", binary)
    return {
        "original_jpeg": original_jpeg,
        "processed_png": png.tobytes() if ok else original_jpeg,
        "gray": enhanced,
        "binary": binary,
        "size": img.size,
    }
