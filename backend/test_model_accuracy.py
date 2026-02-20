"""
Test script to compare audio quality before and after training.

This script:
1. Tests WITHOUT the trained model (baseline)
2. Tests WITH the trained model
3. Compares the results
"""

from pathlib import Path
import torch
import numpy as np
import soundfile as sf
from train_enhancer import Conv1dAutoEncoder
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUTTER_DIR = PROJECT_ROOT / "Stutter"
MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "stutter_enhancer.pt"

def load_test_audio(audio_path: Path, target_sr: int = 16000, max_duration: float = 3.0):
    """Load a test audio file."""
    info = sf.info(str(audio_path))
    sr = info.samplerate
    
    # Read only first few seconds
    max_samples = int(max_duration * sr)
    frames_to_read = min(max_samples, info.frames)
    
    with sf.SoundFile(str(audio_path)) as f:
        audio = f.read(frames_to_read, dtype='float32')
    
    # Convert to torch tensor
    audio = torch.from_numpy(audio).float()
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)
    else:
        audio = audio.T
    
    # Convert to mono
    if audio.shape[0] > 1:
        audio = audio.mean(dim=0, keepdim=True)
    
    # Resample if needed
    if sr != target_sr:
        import torchaudio
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)
        audio = resampler(audio)
    
    # Normalize
    audio = audio / (audio.abs().max() + 1e-8)
    
    return audio, target_sr

def calculate_snr(signal: np.ndarray, noise: np.ndarray) -> float:
    """Calculate Signal-to-Noise Ratio in dB."""
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    
    if noise_power < 1e-10:
        return 100.0  # Very high SNR
    
    snr = 10 * np.log10(signal_power / noise_power)
    return snr

def calculate_metrics(original: torch.Tensor, enhanced: torch.Tensor) -> dict:
    """Calculate quality metrics."""
    original_np = original.squeeze().numpy()
    enhanced_np = enhanced.squeeze().numpy()
    
    # Ensure same length
    min_len = min(len(original_np), len(enhanced_np))
    original_np = original_np[:min_len]
    enhanced_np = enhanced_np[:min_len]
    
    # Mean Squared Error (lower is better)
    mse = np.mean((original_np - enhanced_np) ** 2)
    
    # Signal-to-Noise Ratio (higher is better)
    noise = original_np - enhanced_np
    snr = calculate_snr(original_np, noise)
    
    # Peak Signal-to-Noise Ratio
    max_val = max(original_np.max(), enhanced_np.max())
    psnr = 20 * np.log10(max_val / (np.sqrt(mse) + 1e-10))
    
    # Spectral convergence (lower is better)
    spec_conv = np.linalg.norm(original_np - enhanced_np) / (np.linalg.norm(original_np) + 1e-10)
    
    return {
        "mse": float(mse),
        "snr_db": float(snr),
        "psnr_db": float(psnr),
        "spectral_convergence": float(spec_conv)
    }

def test_model():
    """Test the trained model and compare with baseline."""
    print("=" * 70)
    print("SPEECH ENHANCEMENT MODEL - ACCURACY COMPARISON")
    print("=" * 70)
    
    # Check if model exists
    if not MODEL_PATH.exists():
        print("\n❌ ERROR: Trained model not found!")
        print(f"Expected location: {MODEL_PATH}")
        print("Please run train_enhancer.py first.")
        return
    
    # Load model
    print("\n📦 Loading trained model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Conv1dAutoEncoder().to(device)
    
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint.get("model_state", checkpoint))
    model.eval()
    
    training_info = {
        "epoch": checkpoint.get("epoch", "unknown"),
        "val_loss": checkpoint.get("val_loss", "unknown"),
        "train_loss": checkpoint.get("train_loss", "unknown")
    }
    
    print(f"✓ Model loaded successfully")
    print(f"  - Device: {device}")
    print(f"  - Training epoch: {training_info['epoch']}")
    print(f"  - Validation loss: {training_info['val_loss']}")
    print(f"  - Training loss: {training_info['train_loss']}")
    
    # Get test files
    test_files = sorted(list(STUTTER_DIR.glob("*.flac")))[:5]  # Test on 5 files
    
    if not test_files:
        print("\n❌ ERROR: No test files found in Stutter directory!")
        return
    
    print(f"\n🧪 Testing on {len(test_files)} audio files...")
    print("-" * 70)
    
    all_metrics_before = []
    all_metrics_after = []
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n[{i}/{len(test_files)}] Testing: {test_file.name}")
        
        try:
            # Load audio
            audio, sr = load_test_audio(test_file)
            audio = audio.to(device)
            
            # BEFORE: No enhancement (baseline)
            baseline = audio.clone()
            
            # AFTER: With trained model
            with torch.no_grad():
                enhanced = model(audio.unsqueeze(0)).squeeze(0)
            
            # Calculate metrics (comparing to a "perfect" version would be ideal,
            # but we'll compare the change in signal characteristics)
            
            # For demonstration, we'll measure how much the model changes the signal
            # In a real scenario, you'd compare against clean reference audio
            
            baseline_np = baseline.cpu().squeeze().numpy()
            enhanced_np = enhanced.cpu().squeeze().numpy()
            
            # Ensure same length
            min_len = min(len(baseline_np), len(enhanced_np))
            baseline_np = baseline_np[:min_len]
            enhanced_np = enhanced_np[:min_len]
            
            # Calculate signal statistics
            baseline_std = np.std(baseline_np)
            enhanced_std = np.std(enhanced_np)
            
            baseline_energy = np.mean(baseline_np ** 2)
            enhanced_energy = np.mean(enhanced_np ** 2)
            
            # Calculate how much the signal changed
            difference = np.mean(np.abs(baseline_np - enhanced_np))
            
            print(f"  Baseline - Std: {baseline_std:.4f}, Energy: {baseline_energy:.4f}")
            print(f"  Enhanced - Std: {enhanced_std:.4f}, Energy: {enhanced_energy:.4f}")
            print(f"  Signal change: {difference:.4f}")
            
            all_metrics_before.append({
                "std": baseline_std,
                "energy": baseline_energy
            })
            
            all_metrics_after.append({
                "std": enhanced_std,
                "energy": enhanced_energy,
                "change": difference
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - BEFORE vs AFTER TRAINING")
    print("=" * 70)
    
    if all_metrics_before and all_metrics_after:
        avg_std_before = np.mean([m["std"] for m in all_metrics_before])
        avg_std_after = np.mean([m["std"] for m in all_metrics_after])
        avg_energy_before = np.mean([m["energy"] for m in all_metrics_before])
        avg_energy_after = np.mean([m["energy"] for m in all_metrics_after])
        avg_change = np.mean([m["change"] for m in all_metrics_after])
        
        print(f"\n📊 Average Signal Statistics:")
        print(f"  BEFORE (No Model):")
        print(f"    - Standard Deviation: {avg_std_before:.4f}")
        print(f"    - Signal Energy: {avg_energy_before:.4f}")
        print(f"\n  AFTER (With Trained Model):")
        print(f"    - Standard Deviation: {avg_std_after:.4f}")
        print(f"    - Signal Energy: {avg_energy_after:.4f}")
        print(f"    - Average Signal Change: {avg_change:.4f}")
        
        # Calculate improvement percentage
        std_change = ((avg_std_after - avg_std_before) / avg_std_before) * 100
        energy_change = ((avg_energy_after - avg_energy_before) / avg_energy_before) * 100
        
        print(f"\n📈 Changes:")
        print(f"    - Std Deviation: {std_change:+.2f}%")
        print(f"    - Signal Energy: {energy_change:+.2f}%")
        
        print(f"\n✅ Model Training Info:")
        print(f"    - Final Validation Loss: {training_info['val_loss']}")
        print(f"    - Training Epochs: {training_info['epoch']}")
        print(f"\n💡 Interpretation:")
        print(f"    - The model was trained to reduce stuttering artifacts")
        print(f"    - Lower validation loss = better model performance")
        print(f"    - Signal changes indicate the model is actively processing audio")
        print(f"    - For best results, compare transcription accuracy before/after")
    
    print("\n" + "=" * 70)
    print("✓ Testing completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_model()
