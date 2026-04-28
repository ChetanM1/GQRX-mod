#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np


@dataclass
class PipelineConfig:
    input_path: Path
    output_dir: Path
    sample_rate: float
    center_freq: float


def _read_sigmf_meta(meta_path: Path) -> dict:
    with meta_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_input(input_path: Path, sample_rate: float, center_freq: float) -> Tuple[Path, float, float]:
    """Resolve SigMF/raw input to (data_path, sample_rate, center_freq)."""
    if input_path.is_dir():
        metas = sorted(input_path.glob("*.sigmf-meta"))
        if not metas:
            raise FileNotFoundError(f"No .sigmf-meta files found in {input_path}")
        meta_path = metas[0]
    elif input_path.suffix == ".sigmf-meta":
        meta_path = input_path
    elif input_path.suffix == ".sigmf-data":
        meta_path = input_path.with_suffix(".sigmf-meta")
    else:
        return input_path, sample_rate, center_freq

    if not meta_path.exists():
        raise FileNotFoundError(f"Missing SigMF metadata file: {meta_path}")

    meta = _read_sigmf_meta(meta_path)
    global_meta = meta.get("global", {})

    sr = float(global_meta.get("core:sample_rate", sample_rate))
    cf = float(global_meta.get("core:frequency", center_freq))
    data_path = meta_path.with_suffix(".sigmf-data")
    if not data_path.exists():
        raise FileNotFoundError(f"Missing SigMF data file: {data_path}")
    return data_path, sr, cf


def load_iq(data_path: Path, max_complex_samples: int = 2_000_000) -> np.ndarray:
    """Load interleaved float32 IQ (.sigmf-data/.cfile style)."""
    raw = np.fromfile(data_path, dtype=np.float32)
    if raw.size < 2:
        raise ValueError(f"Input file has no IQ data: {data_path}")
    raw = raw[: (raw.size // 2) * 2]
    iq = raw[0::2] + 1j * raw[1::2]
    if iq.size > max_complex_samples:
        iq = iq[:max_complex_samples]
    return iq


def compute_waterfall(iq: np.ndarray, nfft: int = 1024) -> np.ndarray:
    if iq.size < nfft:
        raise ValueError("Not enough IQ samples for FFT processing.")
    frame_count = iq.size // nfft
    reshaped = iq[: frame_count * nfft].reshape(frame_count, nfft)
    window = np.hanning(nfft).astype(np.float32)
    spec = np.fft.fftshift(np.fft.fft(reshaped * window[None, :], axis=1), axes=1)
    power = np.abs(spec) ** 2
    return 10.0 * np.log10(power + 1e-12)


def estimate_doppler(waterfall_db: np.ndarray, sample_rate: float) -> Tuple[np.ndarray, np.ndarray]:
    nfft = waterfall_db.shape[1]
    peak_bins = np.argmax(waterfall_db, axis=1)
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=1.0 / sample_rate))
    doppler_hz = freqs[peak_bins]
    t = np.arange(waterfall_db.shape[0], dtype=np.float64)
    return t, doppler_hz


def compress_series(t: np.ndarray, y: np.ndarray, factor: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    factor = max(1, factor)
    length = (len(y) // factor) * factor
    if length == 0:
        return t, y
    t2 = t[:length].reshape(-1, factor).mean(axis=1)
    y2 = y[:length].reshape(-1, factor).mean(axis=1)
    return t2, y2


def doppler_to_velocity(doppler_hz: np.ndarray, center_freq: float) -> np.ndarray:
    c = 299_792_458.0
    if center_freq <= 0:
        return np.zeros_like(doppler_hz)
    return (doppler_hz / center_freq) * c
