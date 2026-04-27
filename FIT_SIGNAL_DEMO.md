# Fit Signal Demo (Gqrx)

This demo file is meant to show off the new **Fit** button in the FFT settings panel.

## 1) Generate a demo IQ file

```bash
python3 tools/generate_fit_demo_iq.py ./fit_demo.cfile --sample-rate 1000000 --seconds 12
```

## 2) Start Gqrx on the generated file

```bash
./build/src/gqrx -r -c fit_demo.conf
```

This forces a fresh config and opens the input device dialog.

In the input device dialog, use a file source string like (replace with your real path):

```text
file=/home/<you>/GQRX-mod/fit_demo.cfile,freq=14000000,rate=1000000,repeat=true,throttle=true
```

## 3) Show off the Fit behavior

1. Open **FFT Settings**.
2. Click **Fit**.
3. The view should auto-center and zoom around the strongest signal, reducing empty spectrum space.

## Notes

- Demo format: complex float32 interleaved IQ (`.cfile`).
- If audio is unavailable on your machine, you can still demonstrate visual FFT behavior.
