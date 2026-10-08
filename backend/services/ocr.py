import io
import numpy as np
from PIL import Image

_readers = {}
INDIC = ("ta", "hi", "te", "kn")
TESS = {"ta": "tam", "hi": "hin", "te": "tel", "kn": "kan", "ml": "mal", "en": "eng"}


def _easyocr(image_bytes: bytes, codes: list):
    import easyocr  # lazy: heavy import
    indic = [c for c in codes if c in INDIC]
    langs = [indic[0], "en"] if indic else ["en"]  # EasyOCR allows one Indic script + English
    key = tuple(langs)
    if key not in _readers:
        _readers[key] = easyocr.Reader(list(key), gpu=False, verbose=False)
    img = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    results = _readers[key].readtext(img, detail=1, paragraph=False)
    if not results:
        return "", 0.0
    items = []
    for box, text, conf in results:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append({"t": text, "c": float(conf), "y": sum(ys) / 4, "x": min(xs), "h": max(ys) - min(ys)})
    items.sort(key=lambda i: i["y"])
    rows, cur = [], [items[0]]
    for it in items[1:]:
        if abs(it["y"] - cur[-1]["y"]) < 0.6 * max(it["h"], 10):
            cur.append(it)
        else:
            rows.append(cur)
            cur = [it]
    rows.append(cur)
    text = "\n".join(" ".join(i["t"] for i in sorted(r, key=lambda i: i["x"])) for r in rows)
    return text, sum(i["c"] for i in items) / len(items)


def _tesseract(image_bytes: bytes, codes: list):
    import pytesseract
    langs = "+".join(TESS[c] for c in codes if c in TESS) or "eng"
    if "eng" not in langs:
        langs += "+eng"
    img = Image.open(io.BytesIO(image_bytes))
    d = pytesseract.image_to_data(img, lang=langs, output_type=pytesseract.Output.DICT)
    confs = [float(c) / 100 for c, t in zip(d["conf"], d["text"]) if str(t).strip() and float(c) >= 0]
    text = pytesseract.image_to_string(img, lang=langs).strip()
    return text, (sum(confs) / len(confs) if confs else 0.0)


def recognize(image_bytes: bytes, codes: list) -> dict:
    """Language-aware OCR with automatic fallback. Never raises."""
    errors = []
    if "ml" not in codes:  # EasyOCR has no Malayalam model
        try:
            t, c = _easyocr(image_bytes, codes)
            return {"text": t, "confidence": c, "engine": "EasyOCR", "error": None}
        except Exception as e:
            errors.append(f"EasyOCR: {e}")
    try:
        t, c = _tesseract(image_bytes, codes)
        return {"text": t, "confidence": c, "engine": "Tesseract", "error": None}
    except Exception as e:
        errors.append(f"Tesseract: {e}")
    return {"text": "", "confidence": 0.0, "engine": None, "error": " | ".join(errors)}
