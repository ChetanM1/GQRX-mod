#!/usr/bin/env python3
"""Generate a synthetic SigMF pair for Doppler GUI demonstrations."""

import json
import math
import random
import struct
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    base = out_dir / "r0_waterfall_CF_10.700GHz"

    sr = 256_000
    seconds = 6.0
    n = int(sr * seconds)

    phase0 = 0.0
    phase1 = 0.0
    random.seed(7)

    with (base.with_suffix('.sigmf-data')).open('wb') as f:
        for i in range(n):
            t = i / sr

            f0 = 1200.0 + 900.0 * math.sin(2 * math.pi * 0.15 * t)
            phase0 += 2 * math.pi * f0 / sr
            s0 = complex(math.cos(phase0), math.sin(phase0))

            f1 = -2200.0 + 600.0 * math.sin(2 * math.pi * 0.09 * t + 0.8)
            phase1 += 2 * math.pi * f1 / sr
            s1 = 0.45 * complex(math.cos(phase1), math.sin(phase1))

            noise = complex(random.gauss(0, 0.12), random.gauss(0, 0.12))
            x = s0 + s1 + noise
            f.write(struct.pack('<ff', x.real, x.imag))

    meta = {
        "global": {
            "core:datatype": "cf32_le",
            "core:sample_rate": float(sr),
            "core:version": "1.0.0",
            "core:description": "Synthetic sample for Doppler preprocessing demo",
            "core:author": "GQRX-mod sample generator",
            "core:recorder": "synthetic",
        },
        "captures": [
            {
                "core:sample_start": 0,
                "core:frequency": 10.7e9,
                "core:datetime": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            }
        ],
        "annotations": [],
    }

    with (base.with_suffix('.sigmf-meta')).open('w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    print(f"Generated: {base.with_suffix('.sigmf-meta')}")
    print(f"Generated: {base.with_suffix('.sigmf-data')}")


if __name__ == '__main__':
    main()
