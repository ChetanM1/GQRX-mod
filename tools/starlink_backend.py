#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np


@dataclass
class InputContext:
    input_path: Path
    data_path: Path
    meta_path: Optional[Path]
    sample_rate: float
    center_freq: float
    timestamp: str
    datatype: str


def _read_sigmf_meta(meta_path: Path) -> dict:
    with meta_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_sigmf_pair(input_path: Path) -> Tuple[Path, Path]:
    """Return (meta_path, data_path) for a SigMF input path."""
    if input_path.is_dir():
        metas = sorted(input_path.glob("*.sigmf-meta"))
        if not metas:
            raise FileNotFoundError(f"No .sigmf-meta files found in {input_path}")
        meta_path = metas[0].resolve()
        data_path = meta_path.with_suffix(".sigmf-data")
    elif input_path.suffix == ".sigmf-meta":
        meta_path = input_path.resolve()
        data_path = meta_path.with_suffix(".sigmf-data")
    elif input_path.suffix == ".sigmf-data":
        data_path = input_path.resolve()
        meta_path = data_path.with_suffix(".sigmf-meta")
    else:
        raise ValueError(f"Not a SigMF path: {input_path}")

    if not meta_path.exists():
        raise FileNotFoundError(f"Missing SigMF metadata file: {meta_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Missing SigMF data file: {data_path}")
    return meta_path, data_path


def resolve_input(input_path: Path, sample_rate: float, center_freq: float) -> InputContext:
    """Resolve SigMF/raw input to a normalized processing context."""
    if input_path.suffix in {".sigmf-meta", ".sigmf-data"} or input_path.is_dir():
        meta_path, data_path = _resolve_sigmf_pair(input_path)
        meta = _read_sigmf_meta(meta_path)
        global_meta = meta.get("global", {})
        captures = meta.get("captures", [])
        capture0 = captures[0] if captures else {}

        sr = float(global_meta.get("core:sample_rate", sample_rate))
        cf = float(capture0.get("core:frequency", global_meta.get("core:frequency", center_freq)))
        ts = str(capture0.get("core:datetime", ""))
        dtype = str(global_meta.get("core:datatype", "cf32_le"))
        return InputContext(
            input_path=input_path,
            data_path=data_path,
            meta_path=meta_path,
            sample_rate=sr,
            center_freq=cf,
            timestamp=ts,
            datatype=dtype,
        )

    return InputContext(
        input_path=input_path,
        data_path=input_path,
        meta_path=None,
        sample_rate=sample_rate,
        center_freq=center_freq,
        timestamp="",
        datatype="cf32_le",
    )


def load_iq(data_path: Path, datatype: str, max_complex_samples: int = 2_000_000) -> np.ndarray:
    """Load IQ from SigMF-style datatypes."""
    dt = datatype.lower()
    if dt in {"cf32_le", "cf32"}:
        raw = np.fromfile(data_path, dtype=np.float32)
        raw = raw[: (raw.size // 2) * 2]
        iq = raw[0::2] + 1j * raw[1::2]
    elif dt in {"ci16_le", "ci16"}:
        raw = np.fromfile(data_path, dtype=np.int16)
        raw = raw[: (raw.size // 2) * 2].astype(np.float32) / 32768.0
        iq = raw[0::2] + 1j * raw[1::2]
    elif dt in {"ci8", "ci8_le"}:
        raw = np.fromfile(data_path, dtype=np.int8).astype(np.float32) / 128.0
        raw = raw[: (raw.size // 2) * 2]
        iq = raw[0::2] + 1j * raw[1::2]
    else:
        raise ValueError(f"Unsupported SigMF datatype '{datatype}' for {data_path}")

    if iq.size == 0:
        raise ValueError(f"Input file has no IQ data: {data_path}")

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


def estimate_topk_doppler(waterfall_db: np.ndarray, sample_rate: float, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Estimate Doppler per frame using weighted top-k tones."""
    nfft = waterfall_db.shape[1]
    k = max(1, min(k, nfft))
    freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=1.0 / sample_rate))

    idx = np.argpartition(waterfall_db, -k, axis=1)[:, -k:]
    top_vals = np.take_along_axis(waterfall_db, idx, axis=1)
    weights = np.exp(top_vals - np.max(top_vals, axis=1, keepdims=True))
    selected_freqs = freqs[idx]
    doppler_hz = np.sum(selected_freqs * weights, axis=1) / np.sum(weights, axis=1)
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
