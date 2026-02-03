from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
import torchaudio


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
    Improved encoder-decoder with residual blocks and skip connections
    for better speech enhancement quality.
    """

    def __init__(self) -> None:
        super().__init__()
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
            nn.Conv1d(64, 128, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            ResidualBlock(128, kernel_size=3),
        )
        
        # Decoder with residual blocks
        self.decoder = nn.Sequential(
            ResidualBlock(128, kernel_size=3),
            nn.ConvTranspose1d(128, 64, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            ResidualBlock(64, kernel_size=3),
            nn.ConvTranspose1d(64, 32, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            ResidualBlock(32, kernel_size=3),
            nn.ConvTranspose1d(32, 1, kernel_size=7, stride=2, padding=3, output_padding=1),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
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
    epochs: int = 30,
    batch_size: int = 4,
    lr: float = 2e-4,
    sample_rate: int = 16000,
    segment_seconds: float = 3.0,
    val_split: float = 0.15,
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
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5, verbose=True)
    
    # Combined loss: L1 for waveform + spectral loss for frequency domain
    l1_criterion = nn.L1Loss()
    mse_criterion = nn.MSELoss()

    best_val_loss = float("inf")
    out_dir = PROJECT_ROOT / "backend" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "stutter_enhancer.pt"

    print(f"Training on {DEVICE} with {len(train_ds)} train samples, {len(val_ds)} val samples")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

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
            
            # Combined loss: L1 + spectral
            l1_loss = l1_criterion(enhanced, clear)
            spec_loss = spectral_loss(enhanced, clear)
            loss = l1_loss + 0.3 * spec_loss  # Weight spectral loss
            
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
        
        with torch.no_grad():
            for stutter, clear in val_loader:
                stutter = stutter.to(DEVICE)
                clear = clear.to(DEVICE)
                enhanced = model(stutter)
                
                l1_loss = l1_criterion(enhanced, clear)
                spec_loss = spectral_loss(enhanced, clear)
                loss = l1_loss + 0.3 * spec_loss
                
                val_loss += loss.item() * stutter.size(0)
                val_l1 += l1_loss.item() * stutter.size(0)
                val_spec += spec_loss.item() * stutter.size(0)

        avg_val = val_loss / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0
        avg_val_l1 = val_l1 / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0
        avg_val_spec = val_spec / len(val_loader.dataset) if len(val_loader.dataset) > 0 else 0.0

        scheduler.step(avg_val)
        current_lr = optimizer.param_groups[0]['lr']

        print(f"Epoch {epoch}/{epochs} | LR: {current_lr:.2e}")
        print(f"  Train - Total: {avg_train:.4f} | L1: {avg_l1:.4f} | Spec: {avg_spec:.4f}")
        print(f"  Val   - Total: {avg_val:.4f} | L1: {avg_val_l1:.4f} | Spec: {avg_val_spec:.4f}")

        # Save best model
        if avg_val < best_val_loss:
            best_val_loss = avg_val
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "sample_rate": sample_rate,
                    "segment_seconds": segment_seconds,
                    "epoch": epoch,
                    "val_loss": avg_val,
                },
                model_path,
            )
            print(f"  -> ✓ Saved best model (val loss: {avg_val:.4f}) to {model_path}")


if __name__ == "__main__":
    train()


