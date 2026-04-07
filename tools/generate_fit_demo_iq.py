#!/usr/bin/env python3
"""Generate a synthetic I/Q recording for demonstrating Gqrx 'Fit' button.

The file format is complex float32 interleaved (I,Q), compatible with Gqrx file source.
"""

import argparse
import math
import random
import struct


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demo complex-float I/Q file")
    parser.add_argument("output", help="Output file path (e.g. fit_demo.cfile)")
    parser.add_argument("--sample-rate", type=float, default=1_000_000.0, help="Sample rate in Hz")
    parser.add_argument("--seconds", type=float, default=12.0, help="Duration in seconds")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    fs = args.sample_rate
    n_samples = int(args.seconds * fs)
    rng = random.Random(args.seed)

    # Frequencies relative to center (Hz). One dominant signal + two weaker signals.
    f_dom = 170_000.0
    f_weak_l = -260_000.0
    f_weak_r = 340_000.0

    # Amplitudes (linear)
    a_dom = 0.52
    a_weak_l = 0.06
    a_weak_r = 0.04

    noise_sigma = 0.015

    with open(args.output, "wb") as f:
        for n in range(n_samples):
            t = n / fs

            # Slow fading envelope to make the display dynamic.
            fade = 0.75 + 0.25 * math.sin(2.0 * math.pi * 0.45 * t)

            # Dominant signal with tiny FM-like wobble.
            dom_phase = 2.0 * math.pi * (f_dom * t + 1200.0 * math.sin(2.0 * math.pi * 0.9 * t) / fs)
            i = a_dom * fade * math.cos(dom_phase)
            q = a_dom * fade * math.sin(dom_phase)

            # Two weaker tones farther from center.
            i += a_weak_l * math.cos(2.0 * math.pi * f_weak_l * t)
            q += a_weak_l * math.sin(2.0 * math.pi * f_weak_l * t)

            i += a_weak_r * math.cos(2.0 * math.pi * f_weak_r * t)
            q += a_weak_r * math.sin(2.0 * math.pi * f_weak_r * t)

            # Add noise floor.
            i += rng.gauss(0.0, noise_sigma)
            q += rng.gauss(0.0, noise_sigma)

            # Clamp to avoid huge outliers.
            i = max(-0.99, min(0.99, i))
            q = max(-0.99, min(0.99, q))

            f.write(struct.pack("<ff", i, q))

    print(f"Wrote {n_samples} IQ samples to {args.output}")
    print(f"Sample rate: {fs:.0f} Hz, duration: {args.seconds:.2f}s")


if __name__ == "__main__":
    main()
