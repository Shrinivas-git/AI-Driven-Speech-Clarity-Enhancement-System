## Speech Clarity Enhancement Frontend (React + Vite)

This frontend provides a **modern, minimal, and professional UI** for your Speech Clarity Enhancement System.

### Tech Stack
- **React 18** with **TypeScript**
- **Vite** – fast dev/build tooling
- **WaveSurfer.js** – waveform visualization

### UI Features
- **Dark / Light theme toggle**
- **Upload audio** (FLAC / WAV / MP3)
- **Waveform preview** of the original audio
- **Enhance Speech** button with loading animation
- **Output section**:
  - Play **original** and **enhanced** audio
  - View **cleaned transcript**
  - **Download enhanced audio** as WAV

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

Make sure the **backend FastAPI server** is running on `http://localhost:8000` so that:
- `POST /enhance-speech` and
- `GET /download/{filename}`

are available for the React app.










<<<<<<< HEAD



=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
