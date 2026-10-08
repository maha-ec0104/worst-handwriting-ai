import os
import re
import json
import base64
import time
import requests

LAST_ERROR = {"msg": None}


def num(x) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except Exception:
        return 0.0


def _call(parts: list, as_json: bool):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your_key_here":
        LAST_ERROR["msg"] = "GEMINI_API_KEY is missing"
        return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    cfg = {"temperature": 0.1}
    if as_json:
        cfg["responseMimeType"] = "application/json"
    body = {"contents": [{"parts": parts}], "generationConfig": cfg}
    for attempt in range(2):
        try:
            r = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=90)
            if r.status_code in (429, 500, 503) and attempt == 0:
                time.sleep(2)
                continue
            r.raise_for_status()
            data = r.json()
            return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        except Exception as e:
            LAST_ERROR["msg"] = str(e)[:200]
    return None


def _img(b: bytes, mime="image/jpeg"):
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(b).decode()}}


def _parse(text: str):
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None


def gemini_json(prompt: str, images: list):
    parts = [{"text": prompt}] + [_img(i) for i in images]
    return _parse(_call(parts, True))


def gemini_text(prompt: str):
    return _call([{"text": prompt}], False)


VERIFY_PROMPT = """You are a careful handwriting verification system.
You receive: (1) the ORIGINAL handwritten image, (2) a PREPROCESSED version, (3) raw OCR text (may be wrong),
(4) the detected language, (5) layout hints. Read the ORIGINAL image yourself.

STRICT RULES:
- Keep the SAME language(s) and script as the handwriting. NEVER translate. Preserve code-switching
  (e.g. Tamil + English stays Tamil + English).
- Use document context to fix OCR mistakes ONLY when the original image visually supports the fix.
- If a word is genuinely unclear, write [UNCERTAIN] in its place. If unreadable, write [ILLEGIBLE]. NEVER guess.
- Crossed-out text must NOT appear in "lines". List it in "crossed_out" (with "replaced_by" if a replacement is written).
- Text written outside the main body (margins, side notes) goes in "margin_notes", not in "lines".
- Give each line a confidence 0-1 that the image supports your text.
- "explanation": ONE or TWO short user-friendly sentences. No step-by-step reasoning.

Return ONLY this JSON:
{
 "title": string|null,
 "language": "e.g. Tamil + English",
 "language_confidence": 0-1,
 "lines": [{"text": string, "confidence": 0-1, "type": "title|heading|paragraph|bullet|numbered|table|signature"}],
 "margin_notes": [{"text": string, "confidence": 0-1}],
 "crossed_out": [{"text": string, "replaced_by": string|null, "confidence": 0-1}],
 "uncertain_parts": [{"text": string, "reason": string, "confidence": 0-1}],
 "corrections": [{"from": string, "to": string, "confidence": 0-1}],
 "structure": {"has_table": bool, "tables": [[["cell"]]], "has_signature": bool, "bullet_count": int, "numbered_count": int},
 "explanation": string
}"""


def verify(original: bytes, processed: bytes, raw_text: str, lang: dict, layout: dict):
    prompt = (VERIFY_PROMPT
              + f"\n\nDETECTED LANGUAGE: {lang.get('language')} (confidence {lang.get('confidence')})"
              + f"\nLAYOUT HINTS: {json.dumps(layout)}"
              + f"\nRAW OCR TEXT:\n{raw_text or '(OCR returned nothing - read the image directly)'}")
    parts = [{"text": prompt}, {"text": "ORIGINAL IMAGE:"}, _img(original),
             {"text": "PREPROCESSED IMAGE:"}, _img(processed, "image/png")]
    res = _parse(_call(parts, True))
    return res if isinstance(res, dict) and "lines" in res else None


def answer_query(question: str, document: str):
    prompt = ("Answer the question using ONLY the document text below. If the answer is not in the document, "
              "say 'Not found in the document.' Reply in the language of the question. Be concise.\n\n"
              f"DOCUMENT:\n{document}\n\nQUESTION: {question}")
    return gemini_text(prompt)
