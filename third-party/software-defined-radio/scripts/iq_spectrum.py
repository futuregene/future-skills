#!/usr/bin/env python3
"""Plot a PSD and waterfall of an IQ capture. Writes a PNG if matplotlib is present;
otherwise prints an ASCII spectrum so it still works headless.

Usage:
  python iq_spectrum.py cap.cu8 --fs 2.4e6 --fc 100.1e6 -o spec.png
  python iq_spectrum.py cap.cf32 --fs 8M --format cf32 --nfft 8192
  python iq_spectrum.py cap.cu8 --fs 2.4e6 --ascii
"""
import argparse
import os
import sys

import numpy as np

try:
    from _common import read_iq, guess_format, parse_freq, eng, have_scipy
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import read_iq, guess_format, parse_freq, eng, have_scipy


def psd(iq, fs, nfft):
    if have_scipy():
        from scipy import signal
        f, p = signal.welch(iq, fs, nperseg=min(nfft, len(iq)),
                            return_onesided=False, detrend=False, scaling="density")
        f = np.fft.fftshift(f)
        p = np.fft.fftshift(p)
        return f, 10 * np.log10(p + 1e-30)
    # numpy fallback: average periodogram
    nfft = min(nfft, len(iq))
    nseg = max(1, len(iq) // nfft)
    win = np.hanning(nfft)
    acc = np.zeros(nfft)
    for k in range(nseg):
        seg = iq[k * nfft:(k + 1) * nfft] * win
        acc += np.abs(np.fft.fftshift(np.fft.fft(seg))) ** 2
    acc /= nseg
    f = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / fs))
    return f, 10 * np.log10(acc / (fs * (win ** 2).sum()) + 1e-30)


def ascii_spectrum(f, pdb, fc, width=70, height=20):
    lo, hi = pdb.min(), pdb.max()
    rng = max(hi - lo, 1e-6)
    # bucket into width columns
    idx = np.linspace(0, len(pdb) - 1, width).astype(int)
    cols = pdb[idx]
    fcols = f[idx]
    print("\nPSD (dB), span %s .. %s%s" %
          (eng((fc or 0) + f[0], "Hz"), eng((fc or 0) + f[-1], "Hz"),
           "  center=%s" % eng(fc, "Hz") if fc else ""))
    print("max %.1f dB, min %.1f dB" % (hi, lo))
    for row in range(height, 0, -1):
        thresh = lo + rng * row / height
        line = "".join("#" if c >= thresh else " " for c in cols)
        print("%6.0f |%s" % (thresh, line))
    # axis
    axis = "       " + "-" * width
    print(axis)
    labels = "       %-*s%*s" % (width // 2, eng((fc or 0) + f[0], ""),
                                 width - width // 2, eng((fc or 0) + f[-1], ""))
    print(labels)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("--fs", required=True)
    p.add_argument("--fc", default=None)
    p.add_argument("--format")
    p.add_argument("--nfft", type=int, default=4096)
    p.add_argument("-o", "--out", default=None, help="output PNG (default: <file>.png)")
    p.add_argument("--ascii", action="store_true", help="force ASCII output")
    p.add_argument("--max-samples", type=float, default=8e6)
    a = p.parse_args()

    fmt = guess_format(a.file, a.format)
    if fmt is None:
        print("Cannot infer format; pass --format"); sys.exit(2)
    fs = parse_freq(a.fs)
    fc = parse_freq(a.fc) if a.fc else 0.0

    iq, _ = read_iq(a.file, fmt, count=int(a.max_samples))
    if len(iq) < 16:
        print("too few samples"); sys.exit(1)
    f, pdb = psd(iq, fs, a.nfft)

    use_mpl = (not a.ascii)
    if use_mpl:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.ticker import EngFormatter
        except Exception:
            use_mpl = False

    if not use_mpl:
        ascii_spectrum(f, pdb, fc)
        # crude waterfall stats
        return

    out = a.out or (os.path.splitext(a.file)[0] + ".png")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [1, 1.4]})
    xf = (fc + f)
    ax1.plot(xf, pdb, lw=0.7)
    ax1.set_title("PSD - %s" % os.path.basename(a.file))
    ax1.set_ylabel("dB")
    ax1.grid(alpha=0.3)
    ax1.xaxis.set_major_formatter(EngFormatter(unit="Hz"))

    # spectrogram
    nfft = min(a.nfft, 1024)
    if have_scipy():
        from scipy import signal
        ff, tt, Sxx = signal.spectrogram(iq, fs, nperseg=nfft, noverlap=nfft * 3 // 4,
                                        return_onesided=False, detrend=False)
        ff = np.fft.fftshift(ff)
        Sxx = np.fft.fftshift(10 * np.log10(Sxx + 1e-30), axes=0)
        ax2.imshow(Sxx, aspect="auto", origin="lower",
                   extent=[fc + ff[0], fc + ff[-1], 0, tt[-1]], cmap="viridis")
    else:
        # manual STFT
        step = nfft // 2
        rows = []
        for k in range(0, len(iq) - nfft, step):
            seg = iq[k:k + nfft] * np.hanning(nfft)
            rows.append(np.fft.fftshift(20 * np.log10(np.abs(np.fft.fft(seg)) + 1e-30)))
        Sxx = np.array(rows)
        ax2.imshow(Sxx, aspect="auto", origin="lower",
                   extent=[fc + f[0], fc + f[-1], 0, len(rows)], cmap="viridis")
    ax2.set_title("Waterfall")
    ax2.set_xlabel("frequency")
    ax2.set_ylabel("time")
    ax2.xaxis.set_major_formatter(EngFormatter(unit="Hz"))
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
