import re

MARKER = re.compile(r"\[(?:UNCERTAIN|ILLEGIBLE)[^\]]*\]", re.I)


def clamp(x) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


def level(c: float) -> str:
    if c >= 0.85:
        return "HIGH"
    if c >= 0.60:
        return "MEDIUM"
    return "LOW"


def find_markers(text: str) -> list:
    return MARKER.findall(text or "")


def overall(lines: list, ocr_conf: float, n_uncertain: int) -> float:
    total = sum(len(l["text"]) for l in lines)
    if total:
        base = sum(l["confidence"] * len(l["text"]) for l in lines) / total
    else:
        base = ocr_conf * 0.6
    base -= min(0.15, 0.02 * n_uncertain)
    return clamp(base)
