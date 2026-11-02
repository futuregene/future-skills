#!/usr/bin/env python3
"""Blind estimate of symbol rate and modulation hints for a digital burst.

Method:
  - envelope-spectrum line (FFT of |x|^2) -> symbol rate for shaped/OOK signals
  - x^2 / x^4 / x^8 spectral lines -> PSK order and carrier offset
  - instantaneous-frequency histogram -> FSK level count and deviation
  - autocorrelation of |x| -> burst/frame repetition period

Usage:
  python symbol_rate.py cap.cu8 --fs 2.4e6
  python symbol_rate.py cap.cf32 --fs 1M --format cf32
"""
import argparse
import os
import sys

import numpy as np

try:
    from _common import read_iq, guess_format, parse_freq, eng
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import read_iq, guess_format, parse_freq, eng


def spectral_line(x, fs, exclude_dc_bins=3):
    """Return (freq_of_peak, prominence_db) of the largest FFT line, ignoring DC."""
    n = len(x)
    X = np.abs(np.fft.fftshift(np.fft.fft(x * np.hanning(n))))
    freqs = np.fft.fftshift(np.fft.fftfreq(n, 1 / fs))
    mid = n // 2
    X[mid - exclude_dc_bins:mid + exclude_dc_bins + 1] = 0
    k = np.argmax(X)
    med = np.median(X[X > 0]) + 1e-12
    prom = 20 * np.log10(X[k] / med + 1e-12)
    return freqs[k], prom, X, freqs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("--fs", required=True)
    p.add_argument("--format")
    p.add_argument("--max-samples", type=float, default=2e6)
    a = p.parse_args()

    fmt = guess_format(a.file, a.format)
    if fmt is None:
        print("cannot infer format; pass --format"); sys.exit(2)
    fs = parse_freq(a.fs)
    iq, _ = read_iq(a.file, fmt, count=int(a.max_samples))
    n = len(iq)
    if n < 4096:
        print("need more samples"); sys.exit(1)
    iq = iq - iq.mean()

    print("analyzing %s samples at %s\n" % (f"{n:,}", eng(fs, "Hz")))

    # 1. symbol rate from |x|^2 envelope spectrum
    env = np.abs(iq) ** 2
    env = env - env.mean()
    f_sym, prom, _, _ = spectral_line(env, fs)
    print("== symbol rate (|x|^2 envelope line) ==")
    if prom > 6:
        print("  peak at %s, prominence %.1f dB" % (eng(abs(f_sym), "Hz"), prom))
        print("  -> estimated symbol rate ~ %s (also check harmonics/2)" % eng(abs(f_sym), "Baud"))
    else:
        print("  no strong envelope line (prominence %.1f dB); signal may be continuous-phase"
              " (MSK/GMSK/FM) or unshaped" % prom)

    # 2. PSK order via x^2, x^4, x^8
    print("\n== carrier / PSK order (x^M lines) ==")
    for M in (2, 4, 8):
        xm = iq ** M
        fk, promk, _, _ = spectral_line(xm, fs)
        tag = {2: "BPSK", 4: "QPSK", 8: "8PSK"}[M]
        strong = "STRONG" if promk > 10 else ("weak" if promk > 5 else "-")
        foff = fk / M
        print("  x^%d: line at %s (prom %.1f dB) [%s]  -> if %s: carrier offset ~ %s"
              % (M, eng(abs(fk), "Hz"), promk, strong, tag, eng(foff, "Hz")))

    # 3. FSK: instantaneous frequency histogram
    print("\n== FSK check (instantaneous frequency) ==")
    inst = np.angle(iq[1:] * np.conj(iq[:-1])) * fs / (2 * np.pi)
    inst = inst[np.abs(inst) < fs / 2]
    hist, edges = np.histogram(inst, bins=101)
    centers = (edges[:-1] + edges[1:]) / 2
    # find peaks
    peaks = []
    for i in range(1, len(hist) - 1):
        if hist[i] > hist[i - 1] and hist[i] >= hist[i + 1] and hist[i] > hist.max() * 0.15:
            peaks.append((centers[i], hist[i]))
    peaks.sort(key=lambda t: -t[1])
    peaks = peaks[:4]
    peaks.sort()
    if len(peaks) >= 2:
        levels = [pk[0] for pk in peaks]
        print("  %d frequency level(s): %s" % (len(peaks), ", ".join(eng(l, "Hz") for l in levels)))
        if len(peaks) == 2:
            dev = abs(levels[1] - levels[0]) / 2
            print("  -> looks like 2FSK, deviation ~ %s (spacing %s)" %
                  (eng(dev, "Hz"), eng(abs(levels[1] - levels[0]), "Hz")))
        elif len(peaks) >= 3:
            print("  -> looks like 4FSK/multi-FSK; level spacings suggest deviation")
    else:
        print("  single frequency cluster: not obviously FSK (could be PSK/QAM/OOK/CW)")

    # 4. autocorrelation for burst/frame period
    print("\n== periodicity (autocorrelation of |x|) ==")
    mag = np.abs(iq) - np.abs(iq).mean()
    seg = mag[:min(len(mag), 1 << 17)]
    ac = np.correlate(seg, seg, mode="full")[len(seg) - 1:]
    ac = ac / (ac[0] + 1e-12)
    # find first strong peak after lag 20
    lag_peak = None
    for i in range(20, len(ac) - 1):
        if ac[i] > 0.3 and ac[i] > ac[i - 1] and ac[i] >= ac[i + 1]:
            lag_peak = i
            break
    if lag_peak:
        print("  repetition at lag %d samples = %s (%s)" %
              (lag_peak, eng(lag_peak / fs, "s"), eng(fs / lag_peak, "Hz")))
        print("  -> could be a frame/slot period or a spreading sequence")
    else:
        print("  no strong short-lag periodicity found")

    print("\nHints: compare the symbol rate and level count against references/modulation.md")
    print("section 6, and confirm by demodulating in URH / inspectrum / GNU Radio.")


if __name__ == "__main__":
    main()
