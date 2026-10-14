# FluentUp AI — Complete Local Setup & Run Guide

## System Prerequisites
- **Node.js**: v18.0.0+ (Tested on v24.x)
- **Python**: 3.10+ (Tested on Python 3.14)
- **PowerShell** (Windows) or **Bash / Zsh** (macOS / Linux)

---

## 1. Quick Start (Windows PowerShell)

### Backend Setup
```powershell
cd "c:\Users\VICTUS\OneDrive\Desktop\HARSHIT\Fluent AI\backend"

# (Optional: Create virtual environment if desired)
# python -m venv venv
# .\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend API will be running at:
- **API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/health`

### Frontend Setup
In a second terminal:
```powershell
cd "c:\Users\VICTUS\OneDrive\Desktop\HARSHIT\Fluent AI\frontend"

# Install dependencies (already cached)
npm install

# Start Vite dev server
npm run dev
```
Frontend Web Application will be live at:
- **Web App:** `http://localhost:5173`

---

## 2. macOS / Linux Startup Commands

### Backend:
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 3. Environment Variables Configuration

Both `backend/.env.example` and `frontend/.env.example` are provided.

### Activating Google Gemini (Live LLM Mode):
In `backend/.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### Activating OpenAI Mode:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Zero-Configuration Offline / Test Mode:
If `GEMINI_API_KEY` or `OPENAI_API_KEY` are left blank, FluentUp AI automatically activates its **Deterministic Local Pedagogical Tutor Engine**. All conversation modes, instant grammar corrections, CEFR-aligned test generations, and Hinglish translation work seamlessly without requiring external paid API keys.
