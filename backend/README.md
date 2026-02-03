## Speech Clarity Enhancement Backend (FastAPI)

This backend implements an **ASR → Text Cleaning → TTS** pipeline for stuttered / unclear speech.

### Tech Stack
- **Python 3.10**
- **FastAPI** – REST API framework
- **OpenAI Whisper** – Robust Speech-to-Text
- **Rule-based Text Cleaner** – Removes fillers + repetitions
- **Coqui TTS** – Natural Text-to-Speech
- **Librosa / SoundFile** – Audio preprocessing

### Pipeline
1. **Audio Input** (FLAC/WAV/MP3)
2. **Audio Preprocessing**
   - Convert to mono
   - Resample to 16 kHz
   - Peak normalization
3. **ASR (Whisper)**
   - Handles pauses, repetitions, and disfluencies reasonably well
4. **Intelligent Text Cleaner**
   - Removes fillers like “uh”, “um”, “you know”
   - Collapses immediate word repetitions
   - Fixes simple partial word repetitions (`b-b-because` → `because`)
5. **TTS (Coqui TTS)**
   - Uses a small English model to generate fluent speech
6. **Output**
   - Cleaned transcript (JSON)
   - Clear, enhanced audio file (WAV)

### Main Endpoint
- **POST** `/enhance-speech`
  - **Input**: `file` (audio)
  - **Output (JSON)**:
    - `cleaned_text`: string
    - `enhanced_audio_filename`: filename of synthesized WAV

- **GET** `/download/{filename}`
  - Download enhanced audio by filename.

### Running the Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/docs` for Swagger UI.





