# AI Handwriting Intelligence
Understand • Recognize • Verify • Preserve

Evidence-based handwriting digitization with uncertainty awareness. Output stays in the ORIGINAL language (no translation); Tamil + English code-switching is preserved.

## Architecture
```
Image -> OpenCV preprocessing -> Layout analysis (line count, margin ink)
      -> Language detection (Gemini Vision) -> Language-specific OCR (EasyOCR -> Tesseract fallback)
      -> Gemini Vision verification (original + cleaned image + raw OCR + language + layout)
      -> Confidence engine -> Uncertainty markers -> Structured JSON + clean text
```

## 1. Get a Gemini API key
1. Open https://aistudio.google.com/apikey and sign in. 2. Click "Create API key". 3. Copy it.

## 2. Run the backend (Python 3.10-3.12)
```
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
```
Open `backend/.env` and paste your key after `GEMINI_API_KEY=`.
```
uvicorn main:app --reload --port 8000
```
Check http://localhost:8000/health -> `gemini_key_configured: true`.
If `pip install easyocr` is slow or fails, delete the `easyocr` line: the app falls back to Tesseract, then to Gemini-only reading.

## 3. Run the frontend (Node 18+)
```
cd frontend
npm install
copy .env.example .env         # Mac/Linux: cp .env.example .env
npm run dev
```
Open http://localhost:5173.

## 4. Test
1. Write a messy note, e.g. `நாளைக்கு project submit பண்ண வேண்டும்`, plus a margin word ("Important"), a crossed-out word, and one scribbled word. Photo it.
2. Upload -> Digitize. Check: language badge, same-language text, yellow `[UNCERTAIN]` word, crossed-out and margin sections, confidence.
3. Try the question buttons. Try the exports.
4. Test failure handling: stop the key (blank `.env`) -> you see "AI verification unavailable. Showing raw recognition." Upload a .txt renamed to .jpg -> friendly error.

## 5. GitHub
```
git init
git add .
git commit -m "AI Handwriting Intelligence"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/bad-handwriting-ai.git
git push -u origin main
```
`.env` is git-ignored. Never commit your key.

## 6. Deploy backend on Render
1. render.com -> New -> Web Service -> connect the GitHub repo.
2. Root Directory: `backend`. Runtime: Python 3.
3. Build: `pip install -r requirements.txt`   Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment: add `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`, `ALLOWED_ORIGINS=https://YOUR-APP.vercel.app` (use `*` while testing).
5. Free tier has 512 MB RAM: EasyOCR (PyTorch) may not fit. For Render, remove `easyocr` from requirements.txt; the app then uses Gemini-only reading (Tesseract is not installed on Render by default).
6. Deploy, copy the URL (https://xxxx.onrender.com). The free tier sleeps: open /health once before your demo.

## 7. Deploy frontend on Vercel
1. vercel.com -> Add New Project -> import the repo.
2. Root Directory: `frontend`. Framework: Vite.
3. Environment Variable: `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy. Then put the Vercel URL into Render's `ALLOWED_ORIGINS`.

## 8. Common errors
| Error | Fix |
|---|---|
| `Cannot reach the backend` | Backend not running, or wrong `VITE_API_URL`. Restart `npm run dev` after editing .env |
| `GEMINI_API_KEY is missing` | `.env` must be inside `backend/`, restart uvicorn |
| AI note: 404 / model not found | Set `GEMINI_MODEL` in .env to a current model from aistudio.google.com |
| AI note: 429 | Free quota hit. Wait a minute |
| EasyOCR first run is slow | It downloads models once (needs internet) |
| `TesseractNotFoundError` | Harmless: the app continues with Gemini-only reading |
| CORS error in browser | Add your frontend URL to `ALLOWED_ORIGINS` |
| `pip` fails on numpy/opencv | Use Python 3.11 |

## 9. Two-minute demo script
- 0:00 "Normal OCR turns pixels into characters. We understand the document first."
- 0:20 Upload a messy Tamil + English note. Point at the pipeline steps.
- 0:40 Show Raw recognition (broken) vs AI understood text (clean, still Tamil + English, not translated).
- 1:05 Show the yellow [UNCERTAIN] word: "It refuses to guess what it cannot see."
- 1:20 Show crossed-out vs final content and margin note, separated.
- 1:35 Confidence bar and "Why did AI choose this text?".
- 1:45 Ask "Find dates" / "Summarize this note", then Download DOCX.
- 1:55 "Evidence-based digitization with uncertainty awareness."

## 10. Five slides
1. Problem: bad handwriting, OCR guesses, multilingual India, silent hallucination.
2. Solution: understand -> read -> verify -> flag. Same-language output.
3. Architecture: the pipeline above.
4. Demo screenshots: raw vs verified, uncertain word, crossed-out, margin note.
5. Impact and future: doctors' prescriptions, forms, student notes, archives; future: word-level boxes on the image, fine-tuned Indic HTR, offline mode, human-in-the-loop corrections.

## 11. For judges
- OpenCV: denoise, contrast, adaptive threshold, layout hints. EasyOCR/Tesseract: language-specific raw text. Gemini Vision: language detection, reading the ORIGINAL image, verification, structure. FastAPI + SQLite + React/Bootstrap.
- Innovation: the LLM is told to correct only with visual evidence and to emit [UNCERTAIN]/[ILLEGIBLE] instead of inventing text. Confidence is per line and visible.
- Honest limits: confidence values come from the vision model's self-assessment blended with OCR agreement. Table extraction is a prototype. Crossed-out and margin detection depend on the model.
