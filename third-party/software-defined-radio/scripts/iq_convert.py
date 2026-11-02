#!/usr/bin/env python3
"""Convert between IQ sample formats, with optional frequency shift, decimation, and trim.

Formats (by extension or --in-format/--out-format): cu8 cs8 cs16 cf32 cf64.

Examples:
  python iq_convert.py in.cu8 out.cf32 --fs 2.4e6
  python iq_convert.py in.cu8 out.cf32 --fs 2.4e6 --shift -250e3 --decim 10
  python iq_convert.py in.cf32 out.cu8 --fs 8M --start 1.0 --dur 5.0 --in-format cf32
"""
import argparse
import os
import sys

import numpy as np

try:
    from _common import (read_iq, write_iq, guess_format, parse_freq, eng,
                         file_num_complex, have_scipy, FORMATS)
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import (read_iq, write_iq, guess_format, parse_freq, eng,
                         file_num_complex, have_scipy, FORMATS)


def decimate(iq, factor):
    if factor <= 1:
        return iq
    if have_scipy():
        from scipy import signal
        out = iq
        f = factor
        while f > 1:
            step = min(f, 8)
            out = signal.decimate(out, step, ftype="fir", zero_phase=False)
            f //= step
        if f != 1:  # non-integer leftover (factor wasn't a product of <=8 steps)
            pass
        return out.astype(np.complex64)
    # numpy FIR low-pass then stride
    ntaps = 64 * factor + 1
    n = np.arange(ntaps) - (ntaps - 1) / 2
    h = np.sinc(n / factor) * np.hanning(ntaps)
    h /= h.sum()
    filt = np.convolve(iq, h, mode="same")
    return filt[::factor].astype(np.complex64)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("infile")
    p.add_argument("outfile")
    p.add_argument("--fs", help="input sample rate (needed for --shift/--start/--dur)")
    p.add_argument("--in-format")
    p.add_argument("--out-format")
    p.add_argument("--shift", help="frequency shift in Hz (moves +shift to 0)")
    p.add_argument("--decim", type=int, default=1)
    p.add_argument("--start", type=float, default=0.0, help="start time in seconds")
    p.add_argument("--dur", type=float, default=None, help="duration in seconds")
    p.add_argument("--scale", type=float, default=1.0, help="amplitude scale before writing")
    a = p.parse_args()

    infmt = guess_format(a.infile, a.in_format)
    outfmt = guess_format(a.outfile, a.out_format)
    if infmt is None:
        print("cannot infer input format; pass --in-format"); sys.exit(2)
    if outfmt is None:
        print("cannot infer output format; pass --out-format"); sys.exit(2)

    fs = parse_freq(a.fs) if a.fs else None
    start_sample = 0
    count = -1
    if fs and a.start:
        start_sample = int(a.start * fs)
    if fs and a.dur:
        count = int(a.dur * fs)

    iq, _ = read_iq(a.infile, infmt, count=count, start_sample=start_sample)
    print("read %s samples (%s)" % (f"{len(iq):,}", infmt))

    if a.shift:
        if not fs:
            print("--shift needs --fs"); sys.exit(2)
        sh = parse_freq(a.shift)
        n = np.arange(len(iq))
        iq = (iq * np.exp(-2j * np.pi * sh / fs * n)).astype(np.complex64)
        print("shifted by %s" % eng(sh, "Hz"))

    if a.decim > 1:
        iq = decimate(iq, a.decim)
        if fs:
            fs = fs / a.decim
        print("decimated by %d -> %s samples%s" %
              (a.decim, f"{len(iq):,}", (", new fs %s" % eng(fs, "Hz")) if fs else ""))

    if a.scale != 1.0:
        iq = (iq * a.scale).astype(np.complex64)

    write_iq(a.outfile, iq, outfmt)
    print("wrote %s (%s, %s samples, %s)" %
          (a.outfile, outfmt, f"{len(iq):,}", eng(os.path.getsize(a.outfile), "B")))
    if fs:
        print("output sample rate: %s" % eng(fs, "Hz"))


if __name__ == "__main__":
    main()
