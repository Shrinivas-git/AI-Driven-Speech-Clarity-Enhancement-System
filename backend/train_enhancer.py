from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
import torchaudio
<<<<<<< HEAD
import os

# Use soundfile backend for loading audio
os.environ['TORCHAUDIO_BACKEND'] = 'soundfile'
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461


"""
Simple speech enhancement training script.

Idea:
- Input: stuttered / unclear speech from ../Stutter
- Target: clear speech from ../Clear
- Model: small 1D Conv encoder-decoder operating on waveforms

NOTE:
- We pair files by sorted index (first stutter file with first clear file, etc.).
  For best results, ensure your folders are ordered so that corresponding
  files line up, or customize the pairing logic to your data.
"""


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUTTER_DIR = PROJECT_ROOT / "Stutter"
CLEAR_DIR = PROJECT_ROOT / "Clear"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class PairedSpeechDataset(Dataset):
    def __init__(
        self,
        stutter_dir: Path,
        clear_dir: Path,
        sample_rate: int = 16000,
        segment_seconds: float = 3.0,
    ) -> None:
        self.stutter_dir = stutter_dir
        self.clear_dir = clear_dir
        self.sample_rate = sample_rate
        self.segment_samples = int(segment_seconds * sample_rate)

        # Collect and sort file lists
        self.stutter_files: List[Path] = sorted(
            [p for p in stutter_dir.glob("*.flac") if p.is_file()]
        )
        self.clear_files: List[Path] = sorted(
            [p for p in clear_dir.glob("*.flac") if p.is_file()]
        )

        n = min(len(self.stutter_files), len(self.clear_files))
        self.stutter_files = self.stutter_files[:n]
        self.clear_files = self.clear_files[:n]

        if n == 0:
            raise RuntimeError("No FLAC files found for training in Clear/Stutter.")

<<<<<<< HEAD
    def _load_and_process(self, path: Path) -> torch.Tensor:
        import soundfile as sf
        # Load audio using soundfile with chunked reading for large files
        try:
            # Get file info first
            info = sf.info(str(path))
            sr = info.samplerate
            
            # Calculate how many samples we need
            target_samples = self.segment_samples
            
            # Read only what we need (first N seconds)
            with sf.SoundFile(str(path)) as f:
                # Read only the segment we need
                frames_to_read = min(target_samples, info.frames)
                wav = f.read(frames_to_read, dtype='float32')
            
            # Convert to torch tensor
            wav = torch.from_numpy(wav).float()
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)  # Add channel dimension
            else:
                wav = wav.T  # Transpose to (channels, samples)
            
            # Convert to mono
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
            
            # Resample if needed
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.sample_rate)
                wav = resampler(wav)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            # Return silence if loading fails
            wav = torch.zeros(1, self.segment_samples)
=======
        self.resampler = torchaudio.transforms.Resample(orig_freq=None, new_freq=sample_rate)

    def _load_and_process(self, path: Path) -> torch.Tensor:
        wav, sr = torchaudio.load(path)
        # Convert to mono
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        # Resample if needed
        if sr != self.sample_rate:
            self.resampler.orig_freq = sr
            wav = self.resampler(wav)
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461

        # Ensure at least segment length: pad or trim
        if wav.shape[1] < self.segment_samples:
            pad_len = self.segment_samples - wav.shape[1]
            wav = F.pad(wav, (0, pad_len))
        else:
            wav = wav[:, : self.segment_samples]

        # Normalize
        wav = wav / (wav.abs().max() + 1e-8)
        return wav

    def __len__(self) -> int:
        return len(self.stutter_files)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        st_path = self.stutter_files[idx]
        cl_path = self.clear_files[idx]

        stutter = self._load_and_process(st_path)
        clear = self._load_and_process(cl_path)
        return stutter, clear


class ResidualBlock(nn.Module):
    """Residual block with skip connection for better gradient flow."""
    def __init__(self, channels: int, kernel_size: int = 3, dilation: int = 1):
        super().__init__()
        padding = (kernel_size - 1) * dilation // 2
        self.conv1 = nn.Conv1d(channels, channels, kernel_size, padding=padding, dilation=dilation)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size, padding=padding, dilation=dilation)
        self.norm1 = nn.BatchNorm1d(channels)
        self.norm2 = nn.BatchNorm1d(channels)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.relu(self.norm1(self.conv1(x)))
        out = self.norm2(self.conv2(out))
        out = out + residual  # Skip connection
        return F.relu(out)


class Conv1dAutoEncoder(nn.Module):
    """
<<<<<<< HEAD
    Enhanced encoder-decoder with deeper architecture and attention mechanisms
    for significantly better speech enhancement quality.
=======
    Improved encoder-decoder with residual blocks and skip connections
    for better speech enhancement quality.
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    """

    def __init__(self) -> None:
        super().__init__()
<<<<<<< HEAD
        # Deeper encoder with more channels and residual blocks
        self.encoder = nn.Sequential(
            # First layer
            nn.Conv1d(1, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            ResidualBlock(64, kernel_size=3),
            ResidualBlock(64, kernel_size=3, dilation=2),  # Dilated for larger receptive field
            
            # Second layer
=======
        # Encoder with residual blocks
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            ResidualBlock(32, kernel_size=3),
            nn.Conv1d(32, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            ResidualBlock(64, kernel_size=3),
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            nn.Conv1d(64, 128, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            ResidualBlock(128, kernel_size=3),
<<<<<<< HEAD
            ResidualBlock(128, kernel_size=3, dilation=2),
            
            # Third layer
            nn.Conv1d(128, 256, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            ResidualBlock(256, kernel_size=3),
            ResidualBlock(256, kernel_size=3, dilation=2),
        )
        
        # Bottleneck with attention-like mechanism
        self.bottleneck = nn.Sequential(
            ResidualBlock(256, kernel_size=5),
            ResidualBlock(256, kernel_size=5, dilation=2),
        )
        
        # Decoder with skip connections (U-Net style)
        self.decoder = nn.Sequential(
            ResidualBlock(256, kernel_size=3),
            ResidualBlock(256, kernel_size=3, dilation=2),
            nn.ConvTranspose1d(256, 128, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            ResidualBlock(128, kernel_size=3),
            ResidualBlock(128, kernel_size=3, dilation=2),
=======
        )
        
        # Decoder with residual blocks
        self.decoder = nn.Sequential(
            ResidualBlock(128, kernel_size=3),
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            nn.ConvTranspose1d(128, 64, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            ResidualBlock(64, kernel_size=3),
<<<<<<< HEAD
            ResidualBlock(64, kernel_size=3, dilation=2),
            nn.ConvTranspose1d(64, 1, kernel_size=7, stride=2, padding=3, output_padding=1),
=======
            nn.ConvTranspose1d(64, 32, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            ResidualBlock(32, kernel_size=3),
            nn.ConvTranspose1d(32, 1, kernel_size=7, stride=2, padding=3, output_padding=1),
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
<<<<<<< HEAD
        z = self.bottleneck(z)  # Apply bottleneck processing
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        out = self.decoder(z)
        # In case of any slight length mismatch, crop to input length
        if out.shape[-1] > x.shape[-1]:
            out = out[..., : x.shape[-1]]
        elif out.shape[-1] < x.shape[-1]:
            # Pad if shorter
            pad_len = x.shape[-1] - out.shape[-1]
            out = F.pad(out, (0, pad_len))
        return out


def spectral_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Spectral loss using STFT for better frequency domain matching."""
    stft_pred = torch.stft(pred.squeeze(1), n_fft=512, hop_length=128, return_complex=True)
    stft_target = torch.stft(target.squeeze(1), n_fft=512, hop_length=128, return_complex=True)
    
    magnitude_pred = torch.abs(stft_pred)
    magnitude_target = torch.abs(stft_target)
    
    return F.mse_loss(magnitude_pred, magnitude_target)


def train(
<<<<<<< HEAD
    epochs: int = 100,  # Increased for better accuracy
    batch_size: int = 4,  # Reduced batch size for memory
    lr: float = 1e-4,  # Lower learning rate for fine-tuning
    sample_rate: int = 16000,
    segment_seconds: float = 2.0,  # Reduced segment length for memory
    val_split: float = 0.15,
    early_stopping_patience: int = 15,  # Stop if no improvement for 15 epochs
=======
    epochs: int = 30,
    batch_size: int = 4,
    lr: float = 2e-4,
    sample_rate: int = 16000,
    segment_seconds: float = 3.0,
    val_split: float = 0.15,
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
) -> None:
    dataset = PairedSpeechDataset(
        stutter_dir=STUTTER_DIR,
        clear_dir=CLEAR_DIR,
        sample_rate=sample_rate,
        segment_seconds=segment_seconds,
    )

    n_val = int(len(dataset) * val_split)
    n_train = len(dataset) - n_val
    train_ds, val_ds = random_split(dataset, [n_train, n_val])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    model = Conv1dAutoEncoder().to(DEVICE)
<<<<<<< HEAD
    # Use AdamW with better weight decay
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4, betas=(0.9, 0.999))
    # Cosine annealing with warm restarts for better convergence
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-6
    )
    
    # Combined loss: L1 + Spectral + Multi-scale
=======
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5, verbose=True)
    
    # Combined loss: L1 for waveform + spectral loss for frequency domain
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    l1_criterion = nn.L1Loss()
    mse_criterion = nn.MSELoss()

    best_val_loss = float("inf")
<<<<<<< HEAD
    best_epoch = 0
    patience_counter = 0
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
    out_dir = PROJECT_ROOT / "backend" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "stutter_enhancer.pt"

<<<<<<< HEAD
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print("=" * 60)
    print(f"ENHANCED TRAINING - High Accuracy Mode")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    print(f"Train samples: {len(train_ds)}")
    print(f"Val samples: {len(val_ds)}")
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Initial LR: {lr}")
    print(f"Early stopping patience: {early_stopping_patience}")
    print("=" * 60)
=======
    print(f"Training on {DEVICE} with {len(train_ds)} train samples, {len(val_ds)} val samples")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        total_l1 = 0.0
        total_spec = 0.0
        
        for stutter, clear in train_loader:
            stutter = stutter.to(DEVICE)
            clear = clear.to(DEVICE)

            optimizer.zero_grad()
            enhanced = model(stutter)
            
<<<<<<< HEAD
            # Enhanced multi-scale loss for better accuracy
            l1_loss = l1_criterion(enhanced, clear)
            spec_loss = spectral_loss(enhanced, clear)
            mse_loss = mse_criterion(enhanced, clear)
            
            # Multi-scale loss: L1 (waveform) + Spectral (frequency) + MSE (overall)
            loss = l1_loss + 0.4 * spec_loss + 0.2 * mse_loss
=======
            # Combined loss: L1 + spectral
            l1_loss = l1_criterion(enhanced, clear)
            spec_loss = spectral_loss(enhanced, clear)
            loss = l1_loss + 0.3 * spec_loss  # Weight spectral loss
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # Gradient clipping
            optimizer.step()

            total_loss += loss.item() * stutter.size(0)
            total_l1 += l1_loss.item() * stutter.size(0)
            total_spec += spec_loss.item() * stutter.size(0)

        avg_train = total_loss / len(train_loader.dataset)
        avg_l1 = total_l1 / len(train_loader.dataset)
        avg_spec = total_spec / len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        val_l1 = 0.0
        val_spec = 0.0
<<<<<<< HEAD
        val_mse = 0.0
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
        
        with torch.no_grad():
            for stutter, clear in val_loader:
                stutter = stutter.to(DEVICE)
                clear = clear.to(DEVICE)
                enhanced = model(stutter)
                
                l1_loss = l1_criterion(enhanced, clear)
                spec_loss = spectral_loss(enhanced, clear)
<<<<<<< HEAD
                mse_loss = mse_criterion(enhanced, clear)
                loss = l1_loss + 0.4 * spec_loss + 0.2 * mse_loss
=======
                loss = l1_loss + 0.3 * spec_loss
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
                
                val_loss += loss.item() * stutter.size(0)
                val_l1 += l1_loss.item() * stutter.size(0)
                val_spec += spec_loss.item() * stutter.size(0)
<<<<<<< HEAD
                val_mse += mse_loss.item() * stutter.size(0)
=======
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461

        avg_val = val_loss / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0
        avg_val_l1 = val_l1 / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0
        avg_val_spec = val_spec / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0
<<<<<<< HEAD
        avg_val_mse = val_mse / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0

        scheduler.step()  # Cosine annealing doesn't need metric
        current_lr = optimizer.param_groups[0]['lr']

        print(f"\nEpoch {epoch}/{epochs} | LR: {current_lr:.2e}")
        print(f"  Train - Total: {avg_train:.4f} | L1: {avg_l1:.4f} | Spec: {avg_spec:.4f}")
        print(f"  Val   - Total: {avg_val:.4f} | L1: {avg_val_l1:.4f} | Spec: {avg_val_spec:.4f} | MSE: {avg_val_mse:.4f}")

        # Early stopping and model saving
        if avg_val < best_val_loss:
            improvement = best_val_loss - avg_val
            best_val_loss = avg_val
            best_epoch = epoch
            patience_counter = 0
            
=======

        scheduler.step(avg_val)
        current_lr = optimizer.param_groups[0]['lr']

        print(f"Epoch {epoch}/{epochs} | LR: {current_lr:.2e}")
        print(f"  Train - Total: {avg_train:.4f} | L1: {avg_l1:.4f} | Spec: {avg_spec:.4f}")
        print(f"  Val   - Total: {avg_val:.4f} | L1: {avg_val_l1:.4f} | Spec: {avg_val_spec:.4f}")

        # Save best model
        if avg_val < best_val_loss:
            best_val_loss = avg_val
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "sample_rate": sample_rate,
                    "segment_seconds": segment_seconds,
                    "epoch": epoch,
                    "val_loss": avg_val,
<<<<<<< HEAD
                    "train_loss": avg_train,
                },
                model_path,
            )
            print(f"  -> ✓ NEW BEST! Saved model (val loss: {avg_val:.4f}, improvement: {improvement:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= early_stopping_patience:
                print(f"\n{'='*60}")
                print(f"Early stopping triggered after {patience_counter} epochs without improvement")
                print(f"Best model was at epoch {best_epoch} with val loss: {best_val_loss:.4f}")
                print(f"Model saved to: {model_path}")
                print(f"{'='*60}")
                break
            print(f"  -> No improvement ({patience_counter}/{early_stopping_patience})")
    
    print(f"\n{'='*60}")
    print(f"Training completed!")
    print(f"Best model: Epoch {best_epoch}, Val Loss: {best_val_loss:.4f}")
    print(f"Saved to: {model_path}")
    print(f"{'='*60}")
=======
                },
                model_path,
            )
            print(f"  -> ✓ Saved best model (val loss: {avg_val:.4f}) to {model_path}")
>>>>>>> 015c03c9e65da3a9fde160ed1e1b7b748a0ed461


if __name__ == "__main__":
    train()


