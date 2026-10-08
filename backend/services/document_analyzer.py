import cv2
import numpy as np
from difflib import SequenceMatcher
from . import confidence as conf

STEPS_FULL = ["Image preprocessing", "Layout analysis", "Language detection",
              "Handwriting recognition", "Context understanding",
              "Vision verification", "Confidence analysis"]


def layout_analysis(binary: np.ndarray) -> dict:
    """Simple OpenCV layout hints: text-line count and ink in the page margins."""
    ink = (binary < 128).astype(np.uint8)
    h, w = ink.shape
    rows = ink.sum(axis=1) > (w * 0.01)
    lines, inside = 0, False
    for r in rows:
        if r and not inside:
            lines += 1
        inside = bool(r)
    left = ink[:, : int(w * 0.12)].mean()
    right = ink[:, int(w * 0.88):].mean()
    return {
        "estimated_lines": int(lines),
        "ink_coverage": round(float(ink.mean()), 4),
        "ink_in_left_margin": bool(left > 0.02),
        "ink_in_right_margin": bool(right > 0.02),
    }


def build_result(lang, ocr_res, ai, layout, steps, warnings) -> dict:
    raw_text = ocr_res.get("text", "") or ""
    ocr_conf = float(ocr_res.get("confidence", 0) or 0)

    if ai:
        lines = [l for l in ai.get("lines", []) if str(l.get("text", "")).strip()]
        for l in lines:
            l["confidence"] = conf.clamp(l.get("confidence", 0.5))
            l["level"] = conf.level(l["confidence"])
        corrected = "\n".join(l["text"] for l in lines)
        uncertain = ai.get("uncertain_parts", []) or []
        # also catch markers the model left in text but forgot to list
        for m in conf.find_markers(corrected):
            if not any(m in str(u.get("text", "")) for u in uncertain):
                uncertain.append({"text": m, "reason": "Marked unclear in text", "confidence": 0.3})
        overall = conf.overall(lines, ocr_conf, len(uncertain))
        language = ai.get("language") or lang.get("language") or "Language uncertain"
        lang_conf = conf.clamp(ai.get("language_confidence", lang.get("confidence", 0)))
        explanation = ai.get("explanation") or "Text was verified against the original image."
        title = ai.get("title")
        structure = ai.get("structure") or {}
        margin = ai.get("margin_notes", []) or []
        crossed = ai.get("crossed_out", []) or []
        corrections = ai.get("corrections", []) or []
    else:
        warnings.append("AI verification unavailable. Showing raw recognition.")
        capped = min(ocr_conf, 0.55)
        lines = [{"text": t, "confidence": capped, "level": conf.level(capped), "type": "paragraph"}
                 for t in raw_text.splitlines() if t.strip()]
        corrected, uncertain, margin, crossed, corrections = raw_text, [], [], [], []
        overall = capped
        language = lang.get("language") or "Language uncertain"
        lang_conf = conf.clamp(lang.get("confidence", 0))
        explanation = "AI verification unavailable. Showing raw recognition."
        title, structure = None, {}

    structure = dict(structure)
    structure["layout_hints"] = layout
    return {
        "success": True,
        "detected_language": language,
        "language_confidence": round(lang_conf, 2),
        "raw_text": raw_text,
        "corrected_text": corrected,
        "lines": lines,
        "confidence": round(overall, 2),
        "confidence_level": conf.level(overall),
        "ocr_agreement": round(SequenceMatcher(None, raw_text, corrected).ratio(), 2) if raw_text else 0,
        "ocr_engine": ocr_res.get("engine"),
        "uncertain_parts": uncertain,
        "crossed_out": crossed,
        "margin_notes": margin,
        "corrections": corrections,
        "title": title,
        "explanation": explanation,
        "document_structure": structure,
        "processing_steps": steps,
        "warnings": warnings,
    }
