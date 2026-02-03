# Speech Clarity Enhancement - Quick Start Guide

## 🚀 Starting the Application

### Step 1: Start Backend Server

Open a terminal/PowerShell in the project root and run:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**OR** double-click `backend/start_server.bat`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Speech Clarity Enhancement API Starting...
```

### Step 2: Start Frontend Server

Open a **NEW** terminal/PowerShell and run:

```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v6.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Step 3: Open in Browser

Open `http://localhost:5173` in your browser.

The frontend will automatically check if the backend is running. If you see "Backend server is offline", make sure Step 1 completed successfully.

## ✅ Verification

1. **Backend Health Check**: Open `http://localhost:8000/health` - should return `{"status":"ok","message":"Backend is running"}`
2. **Frontend**: Should show "Backend is online" (or automatically connect)

## 🔧 Troubleshooting

### Backend won't start?
- Make sure Python 3.10+ is installed
- Activate virtual environment: `backend\.venv\Scripts\activate`
- Install dependencies: `pip install -r backend/requirements.txt`

### Frontend shows "Backend is offline"?
- Check if backend is running on port 8000
- Check backend terminal for errors
- Try refreshing the page (frontend checks every 10 seconds)

### Processing takes too long?
- Audio files are limited to 30 seconds
- Check backend console for progress logs
- Processing should complete within 2 minutes

## 📝 Notes

- Backend runs on: `http://localhost:8000`
- Frontend runs on: `http://localhost:5173`
- Audio files are saved in: `backend/media/`


