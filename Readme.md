# 🌿 KrishiDoc — Crop Disease Advisor

A chatbot that analyzes crop images using **Gemini 1.5 Flash** and provides:
- Disease identification
- Cure & treatment steps
- Precautions & prevention tips
- Severity assessment

## Project Structure

```
crop-disease-bot/
├── backend/
│   ├── app.py            # Flask API server
│   └── requirements.txt
└── frontend/
    └── index.html        # Standalone HTML UI
```

---

## ⚙️ Backend Setup

### 1. Get Gemini API Key
Go to → https://aistudio.google.com/app/apikey and create a free key.

### 2. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set your API key

**Option A — Environment variable (recommended):**
```bash
export GEMINI_API_KEY="your_key_here"
python app.py
```

**Option B — Edit app.py directly:**
```python
GEMINI_API_KEY = "your_key_here"   # line 12 in app.py
```

### 4. Run the server
```bash
python app.py
# Server starts at http://localhost:5000
```

---

## 🖥️ Frontend Setup

Just open `frontend/index.html` in your browser — no build step needed.

> If backend is on a different host/port, update `BACKEND_URL` in `index.html`:
> ```js
> const BACKEND_URL = "http://localhost:5000";  // change this
> ```

---

## API Endpoints

| Method | Endpoint   | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/health`  | Check if server is running           |
| POST   | `/analyze` | Analyze image + optional text        |
| POST   | `/chat`    | Text-only follow-up questions        |

### `/analyze` Request Body
```json
{
  "message": "What disease is this?",
  "image": "<base64 string>",
  "history": []
}
```

---

## 🚀 Deployment Tips

- **Backend**: Deploy on Render, Railway, or a VPS. Set `GEMINI_API_KEY` as env variable.
- **Frontend**: Host on GitHub Pages, Netlify, or Vercel (it's a single HTML file).
- Update `BACKEND_URL` in `index.html` to your deployed backend URL.

---

## Tech Stack
- **Backend**: Python, Flask, Google Generative AI SDK (Gemini 1.5 Flash)
- **Frontend**: Vanilla HTML/CSS/JS (zero dependencies, no build step)