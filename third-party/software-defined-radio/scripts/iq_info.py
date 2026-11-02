#!/usr/bin/env python3
"""Inspect an IQ capture: format, sample count, duration, DC offset, clipping,
RMS/peak level, occupied bandwidth, and the strongest frequency component.

Usage:
  python iq_info.py cap.cu8 --fs 2.4e6 --fc 433.92e6
  python iq_info.py cap.cf32 --fs 8M --format cf32
"""
import argparse
import os
import sys

import numpy as np

try:
    from _common import read_iq, guess_format, file_num_complex, parse_freq, eng, FORMATS
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import read_iq, guess_format, file_num_complex, parse_freq, eng, FORMATS


def occupied_bw(iq, fs, frac_db=20.0):
    """Occupied bandwidth where PSD is within frac_db of the peak (crude)."""
    n = min(len(iq), 1 << 18)
    x = iq[:n] * np.hanning(n)
    P = np.abs(np.fft.fftshift(np.fft.fft(x))) ** 2
    P /= P.max() + 1e-30
    Pdb = 10 * np.log10(P + 1e-30)
    freqs = np.fft.fftshift(np.fft.fftfreq(n, 1 / fs))
    mask = Pdb > -frac_db
    if not mask.any():
        return 0.0, 0.0
    lo, hi = freqs[mask][0], freqs[mask][-1]
    peak_f = freqs[np.argmax(P)]
    return hi - lo, peak_f


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("--fs", help="sample rate (Hz or 2.4M)")
    p.add_argument("--fc", help="center frequency (Hz or 433.92M)")
    p.add_argument("--format", help="cu8|cs8|cs16|cf32|cf64 (else inferred from extension)")
    p.add_argument("--max-samples", type=float, default=4e6, help="how many complex samples to load")
    a = p.parse_args()

    fmt = guess_format(a.file, a.format)
    if fmt is None:
        print("Cannot infer format from extension; pass --format. Known: cu8 cs8 cs16 cf32 cf64")
        sys.exit(2)

    total_samples = file_num_complex(a.file, fmt)
    fs = parse_freq(a.fs) if a.fs else None
    fc = parse_freq(a.fc) if a.fc else None

    iq, _ = read_iq(a.file, fmt, count=int(a.max_samples))
    n = len(iq)

    print("file            : %s" % a.file)
    print("format          : %s (%d bytes/complex sample)" % (fmt, FORMATS[fmt][1]))
    print("size on disk    : %s" % eng(os.path.getsize(a.file), "B"))
    print("total samples   : %s complex" % f"{total_samples:,}")
    if fs:
        print("sample rate     : %s" % eng(fs, "Hz"))
        print("duration        : %s" % eng(total_samples / fs, "s"))
    print("analyzed        : %s complex samples" % f"{n:,}")

    i, q = iq.real, iq.imag
    dc = complex(i.mean(), q.mean())
    rms = np.sqrt(np.mean(np.abs(iq) ** 2))
    peak = np.max(np.abs(iq))
    print("\n-- levels (unit-scaled, full scale ~1.0) --")
    print("DC offset       : I=%+.4f Q=%+.4f  |DC|=%.4f%s" %
          (dc.real, dc.imag, abs(dc), "  (significant, tune off-center)" if abs(dc) > 0.05 else ""))
    print("RMS             : %.4f (%.1f dBFS)" % (rms, 20 * np.log10(rms + 1e-30)))
    print("peak            : %.4f (%.1f dBFS)" % (peak, 20 * np.log10(peak + 1e-30)))
    crest = 20 * np.log10((peak + 1e-30) / (rms + 1e-30))
    print("crest factor    : %.1f dB" % crest)

    # clipping detection depends on format full-scale
    clip_thresh = {"cu8": 0.99, "cs8": 0.99, "cs16": 0.995, "cf32": 0.999, "cf64": 0.999}[fmt]
    clipped = np.mean((np.abs(i) > clip_thresh) | (np.abs(q) > clip_thresh)) * 100
    print("clipping        : %.3f%% of samples near full scale%s" %
          (clipped, "  <-- REDUCE GAIN" if clipped > 0.1 else ""))
    if rms < 0.02:
        print("                  signal very weak; increase gain or check antenna")

    if fs:
        bw, peak_f = occupied_bw(iq, fs)
        print("\n-- spectrum --")
        print("occupied BW(-20dB): %s" % eng(bw, "Hz"))
        print("strongest offset  : %+s from center" % eng(peak_f, "Hz"))
        if fc:
            print("strongest absolute: %s" % eng(fc + peak_f, "Hz"))
        # rough estimate of needed fs
        if bw > 0:
            print("suggest fs >= %s to contain this signal with margin" % eng(bw * 1.25, "Hz"))

    if not fs:
        print("\n(pass --fs for duration, bandwidth, and frequency analysis)")


if __name__ == "__main__":
    main()
