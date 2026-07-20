# MirrorMe 🪞
### *Your skin knows what to wear. We just listen.*

**Live Demo:** https://frontend-plum-nu-bkt57sgnz5.vercel.app  
**Backend API:** https://mirrorme-re5a.onrender.com  
**Demo Video:** [YouTube Link — add after recording]  
**Built for:** YouCam API Skin AI & Apparel VTO Hackathon 2026

---

## The Problem

Every year, shoppers return over $550 billion worth of clothing — not because it was the wrong size, but because it didn't look right *on them*. Try-on apps show you the garment. Skin apps analyze your face. Nobody has ever connected the two into one unified intelligence.

**MirrorMe is the first platform to treat skin health and clothing choice as a single, co-dependent decision.**

---

## What MirrorMe Does

MirrorMe is an agentic AI styling platform that:

1. **Reads your skin** using YouCam's Skin AI API — analyzing radiance, redness, moisture, texture, acne, and oiliness from a single selfie
2. **Reasons across your skin data** using an LLM agent that applies color theory, neckline compatibility, and fabric science to your real skin scores
3. **Curates 3 garment recommendations** with confidence scores and plain-language explanations of why each garment works for your skin *today*
4. **Renders each look on you** using YouCam's generative Apparel VTO API — so you see yourself wearing the AI-curated outfit, not a model

The agent's reasoning is visible. The connection between your skin and your clothing is explicit. This is not two features side by side — it is one unified intelligence.

---

## YouCam APIs Used

| API | Endpoint | Purpose |
|-----|----------|---------|
| YouCam Skin AI | `POST /s2s/v2.0/task/skin-analysis` | Analyzes 7 skin dimensions from selfie |
| YouCam Apparel VTO v3 | `POST /s2s/v2.0/task/cloth-v3` | Renders garment onto user photo |

### Skin AI Fields Used for Agent Reasoning
- `radiance` — determines color boldness recommendation
- `redness` — determines color temperature recommendation  
- `moisture` — determines fabric type recommendation
- `acne` — determines pattern vs solid recommendation
- `texture` — informs overall styling confidence
- `oiliness` — determines fabric finish recommendation
- `all.score` — overall skin health for confidence messaging

---

## Technical Architecture

```
[User Selfie]
      │
      ▼
[YouCam Skin AI API]
      │
      ▼ (7 skin dimension scores)
[MirrorMe Style Agent - Groq LLaMA 3.3 70B]
      │ Applies color theory + skin science rules
      ▼
[3 Ranked Garment Recommendations + Explanations]
      │
      ▼ (user selects garment)
[YouCam Apparel VTO API v3]
      │
      ▼
[Before/After Try-On Result]
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Axios, CSS3 |
| Backend | FastAPI, Python 3.13 |
| Skin Analysis | YouCam Skin AI API (SD mode) |
| Virtual Try-On | YouCam Apparel VTO API v3 |
| Style Agent | Groq API — LLaMA 3.3 70B Versatile |
| Image Processing | Pillow (auto-resize for API requirements) |
| Frontend Deploy | Vercel |
| Backend Deploy | Render.com |

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- YouCam API key (get free at yce.makeupar.com)
- Groq API key (get free at console.groq.com)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
echo YOUCAM_API_KEY=your_key_here > .env
echo GROQ_API_KEY=your_key_here >> .env

uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Open `http://localhost:3000`

---

## Agent Reasoning Logic

The MirrorMe agent applies these rules to real YouCam skin scores:

```
Radiance > 75  → Bold jewel tones amplify natural glow
Radiance < 50  → Soft ivory, blush, cream tones recommended
Redness < 50   → Cool blues and greens counterbalance inflammation
Moisture < 50  → Avoid satin/sheen; recommend matte linen or cotton
Acne < 50      → Solid colors over busy prints
Overall > 75   → Bold choices encouraged — skin is performing well
Overall < 50   → Soft, flattering, forgiving tones recommended
```

---

## User Flow

1. **Upload** — User takes a clear upper-body selfie
2. **Analyze** — YouCam Skin AI scans 7 skin dimensions
3. **Recommend** — Agent reasons across scores and curates 3 looks
4. **Try On** — YouCam VTO renders each look onto the user's photo
5. **Result** — Before/after comparison with agent explanation

---

## The Non-Obvious Insight

Beauty and fashion decisions rarely happen in isolation. What someone wears and how their skin looks are part of the same self-image — and the same purchase moment. A person recovering from a rosacea flare chooses higher necklines. Someone with high radiance today wants to wear something that shows it. These are real, documented consumer behaviors that no single platform has ever addressed as a unified workflow.

MirrorMe addresses this at the API level — not as a UX feature, but as a reasoning architecture.

---

## Screenshots

[Add screenshots after recording demo]
- Skin analysis results with scores
- Three garment recommendations  
- Before/after VTO result

---

## Developer

**Ekpenyong Mfon**  
Statistician & AI Developer | University of Calabar Teaching Hospital  
GitHub: github.com/ekpenyongasuquo  
Upwork: Rising Talent | Healthcare AI Specialist

---

## License

MIT License — see LICENSE file for details.

---

*Built with YouCam API for the YouCam API Skin AI & Apparel VTO Hackathon 2026*