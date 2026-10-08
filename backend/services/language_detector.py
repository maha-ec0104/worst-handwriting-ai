from . import vision_ai

CODES = {"tamil": "ta", "english": "en", "hindi": "hi", "telugu": "te",
         "kannada": "kn", "malayalam": "ml"}

PROMPT = """Look at this handwritten image. Identify every language/script written in it.
Supported: Tamil, English, Hindi, Telugu, Kannada, Malayalam (mixed writing is possible).
Return ONLY JSON: {"languages": ["Tamil","English"], "primary": "Tamil", "confidence": 0.0-1.0}
If the script is not one of these, put the best guess in "languages" and lower the confidence."""


def detect(image_jpeg: bytes) -> dict:
    res = vision_ai.gemini_json(PROMPT, [image_jpeg])
    if not res:
        return {"language": "Language uncertain", "languages": [], "codes": [], "confidence": 0.0,
                "note": "Language uncertain - using multilingual processing."}
    langs = [str(x) for x in res.get("languages", []) if x]
    conf = vision_ai.num(res.get("confidence", 0))
    codes = [CODES[l.lower()] for l in langs if l.lower() in CODES]
    if conf < 0.5 or not langs:
        return {"language": "Language uncertain", "languages": langs, "codes": codes, "confidence": conf,
                "note": "Language uncertain - using multilingual processing."}
    return {"language": " + ".join(langs), "languages": langs, "codes": codes, "confidence": conf, "note": ""}
