# Sample SigMF Demo Dataset

This folder contains a generator for a synthetic SigMF recording pair used to test the end-to-end Gqrx + Python Doppler flow.

Generate files first:

```bash
python3 data/sample_sigmf_demo/generate_sample_sigmf.py
```

This creates:

- `r0_waterfall_CF_10.700GHz.sigmf-meta`
- `r0_waterfall_CF_10.700GHz.sigmf-data`

## Dataset properties

- Center frequency: 10.700 GHz
- Sample rate: 256 kS/s
- Duration: ~6 seconds
- Signal content: synthetic moving tones + noise intended to create non-static Doppler features.

## Full GUI showcase flow

1. Start Gqrx and open **Tools → Run Doppler Preprocessing**.
2. Select this folder: `data/sample_sigmf_demo`.
3. Wait for preprocessing to finish.
4. When prompted, click **Yes** to open **Show Doppler Velocity Waterfall**.
   - Or open manually via **Tools → Show Doppler Velocity Waterfall**.
5. In the velocity window:
   - `Capture Directory` should point to this folder.
   - Click **Scan**.
   - Select the listed band and waterfall record.
   - Click **Plot**.
6. (Optional) Adjust display ranges (`dB Min`, `dB Max`, colormap) and click **Save Figure**.

## Optional direct CLI launch

From repository root:

```bash
python3 data/sample_sigmf_demo/generate_sample_sigmf.py
python3 demo.py --velocity-waterfall data/sample_sigmf_demo
```
