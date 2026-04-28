#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from starlink_backend import (
    compress_series,
    compute_waterfall,
    doppler_to_velocity,
    estimate_topk_doppler,
    load_iq,
    resolve_input,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Starlink Doppler analysis pipeline.")
    p.add_argument("--input", required=True, help="IQ file, .sigmf-meta/.sigmf-data, or SigMF directory")
    p.add_argument("--output", required=True, help="Output directory for generated artifacts")
    p.add_argument("--sample-rate", type=float, default=1_000_000.0, help="Sample rate (Hz)")
    p.add_argument("--center-freq", type=float, default=0.0, help="Center frequency (Hz)")
    return p.parse_args()


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    ctx = resolve_input(input_path, args.sample_rate, args.center_freq)
    iq = load_iq(ctx.data_path, ctx.datatype)
    waterfall_db = compute_waterfall(iq)
    t, doppler_hz = estimate_topk_doppler(waterfall_db, ctx.sample_rate, k=5)
    t_comp, doppler_comp = compress_series(t, doppler_hz, factor=16)
    velocity = doppler_to_velocity(doppler_comp, ctx.center_freq)

    # Waterfall plot
    water_png = output_dir / "waterfall.png"
    plt.figure(figsize=(10, 4))
    plt.imshow(waterfall_db.T, aspect="auto", origin="lower", cmap="viridis")
    plt.title("Starlink Waterfall")
    plt.xlabel("Frame")
    plt.ylabel("FFT Bin")
    plt.colorbar(label="Power (dB)")
    plt.tight_layout()
    plt.savefig(water_png, dpi=150)
    plt.close()

    # Doppler compression data
    doppler_csv = output_dir / "doppler_compressed.csv"
    np.savetxt(
        doppler_csv,
        np.column_stack([t_comp, doppler_comp]),
        delimiter=",",
        header="frame,doppler_hz",
        comments="",
    )

    # Velocity plot
    vel_png = output_dir / "velocity.png"
    plt.figure(figsize=(10, 4))
    plt.plot(t_comp, velocity)
    plt.title("Estimated Relative Velocity")
    plt.xlabel("Frame")
    plt.ylabel("Velocity (m/s)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(vel_png, dpi=150)
    plt.close()

    print(f"RESULT_DIR: {output_dir}")
    if ctx.meta_path:
        print(f"META_PATH: {ctx.meta_path}")
    print(f"DATA_PATH: {ctx.data_path}")
    print(f"SAMPLE_RATE_HZ: {ctx.sample_rate}")
    print(f"CENTER_FREQ_HZ: {ctx.center_freq}")
    print(f"CAPTURE_TIMESTAMP: {ctx.timestamp}")
    print(f"WATERFALL_PNG: {water_png}")
    print(f"DOPPLER_CSV: {doppler_csv}")
    print(f"VELOCITY_PNG: {vel_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
