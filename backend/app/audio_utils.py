"""
Audio preprocessing utilities.

Steps:
- Load audio file
- Convert to mono
- Resample to 16 kHz
- Normalize volume
"""

from pathlib import Path
from typing import Tuple

import librosa
import numpy as np
import soundfile as sf

TARGET_SR = 16000

# Safety limit: cap audio length to avoid huge arrays that can crash NumPy / Whisper.
# You can increase this if you want to handle longer utterances.
MAX_DURATION_SECONDS = 30.0


def load_and_preprocess(audio_path: Path) -> Tuple[np.ndarray, int]:
    """
    Load an audio file and apply required preprocessing:
    - Supports multiple formats: WAV, FLAC, MP3, WebM, OGG
    - mono
    - resample to 16k
    - peak normalization
    - truncate to a safe maximum duration to avoid enormous arrays
    """
    try:
        # librosa can handle WebM, but we need to ensure it's supported
        # If WebM fails, try converting or use alternative loader
        y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    except Exception as e:
        # If librosa fails (e.g., WebM codec issue), try with ffmpeg backend
        try:
            import warnings
            warnings.filterwarnings("ignore")
            # Try with different backend or format
            y, sr = librosa.load(str(audio_path), sr=None, mono=True, format='wav')
        except Exception as e2:
            # Last resort: try to load as any format
            raise RuntimeError(
                f"Could not load audio file {audio_path.name}. "
                f"Supported formats: WAV, FLAC, MP3, WebM. Error: {e}"
            )

    # First truncate in the *original* sampling rate to avoid creating
    # enormous intermediate arrays for very long recordings.
    max_raw_samples = int(MAX_DURATION_SECONDS * sr)
    if y.shape[0] > max_raw_samples:
        y = y[:max_raw_samples]

    # Resample if needed
    if sr != TARGET_SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR

    # Extra safety: enforce limit again after resampling
    max_samples = int(MAX_DURATION_SECONDS * TARGET_SR)
    if y.shape[0] > max_samples:
        y = y[:max_samples]

    # Simple peak normalization
    peak = np.max(np.abs(y)) or 1.0
    y = y / peak

    return y, sr


def save_wav(y: np.ndarray, sr: int, out_path: Path):
    """
    Save waveform to WAV using soundfile.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_path), y, sr)





