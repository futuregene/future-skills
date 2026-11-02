#!/usr/bin/env python3
"""Demodulate WBFM / NBFM / AM from an IQ file to a WAV audio file.

Examples:
  python fm_demod.py cap.cu8 --fs 2.4e6 --mode wbfm -o out.wav
  python fm_demod.py cap.cu8 --fs 2.4e6 --offset 250e3 --mode nbfm -o out.wav
  python fm_demod.py cap.cf32 --fs 1M --mode am --format cf32 -o out.wav

Needs numpy; uses scipy if available for better filtering (recommended).
De-emphasis default 50 us (EU/Indonesia/most of world); use --deemph 75e-6 for the Americas.
"""
import argparse
import os
import sys
import wave

import numpy as np

try:
    from _common import read_iq, guess_format, parse_freq, eng, have_scipy
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import read_iq, guess_format, parse_freq, eng, have_scipy


def lowpass(x, fs, cutoff, numtaps=127):
    if have_scipy():
        from scipy import signal
        b = signal.firwin(numtaps, cutoff / (fs / 2))
        return signal.lfilter(b, 1, x)
    n = np.arange(numtaps) - (numtaps - 1) / 2
    h = np.sinc(2 * cutoff / fs * n) * np.hanning(numtaps)
    h /= h.sum()
    return np.convolve(x, h, mode="same")


def resample_to(x, fs_in, fs_out):
    if have_scipy():
        from scipy import signal
        from math import gcd
        g = gcd(int(fs_in), int(fs_out))
        up = int(fs_out) // g
        down = int(fs_in) // g
        # keep the up/down factors sane
        if up > 2000 or down > 2000:
            # fall back to simple interpolation
            n_out = int(len(x) * fs_out / fs_in)
            xp = np.linspace(0, len(x) - 1, n_out)
            return np.interp(xp, np.arange(len(x)), x)
        return signal.resample_poly(x, up, down)
    n_out = int(len(x) * fs_out / fs_in)
    xp = np.linspace(0, len(x) - 1, n_out)
    return np.interp(xp, np.arange(len(x)), x)


def deemphasis(x, fs, tau):
    if tau <= 0:
        return x
    # single-pole IIR
    dt = 1.0 / fs
    alpha = dt / (tau + dt)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = acc + alpha * (x[i] - acc)
        y[i] = acc
    return y


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("--fs", required=True)
    p.add_argument("--mode", choices=["wbfm", "nbfm", "am"], default="wbfm")
    p.add_argument("--offset", default="0", help="signal offset from center (Hz)")
    p.add_argument("--format")
    p.add_argument("--audio-rate", type=int, default=48000)
    p.add_argument("--deemph", type=float, default=50e-6, help="de-emphasis tau (s); 0 to disable")
    p.add_argument("--max-samples", type=float, default=2e7)
    p.add_argument("-o", "--out", default="demod.wav")
    a = p.parse_args()

    fmt = guess_format(a.file, a.format)
    if fmt is None:
        print("cannot infer format; pass --format"); sys.exit(2)
    fs = parse_freq(a.fs)
    offset = parse_freq(a.offset)

    iq, _ = read_iq(a.file, fmt, count=int(a.max_samples))
    print("read %s samples at %s" % (f"{len(iq):,}", eng(fs, "Hz")))

    # shift signal to baseband
    if offset:
        n = np.arange(len(iq))
        iq = iq * np.exp(-2j * np.pi * offset / fs * n)

    if a.mode == "wbfm":
        target_if = 240000.0
        aud_cut = 15000.0
    elif a.mode == "nbfm":
        target_if = 48000.0
        aud_cut = 4000.0
    else:  # am
        target_if = 48000.0
        aud_cut = 5000.0

    # decimate to IF rate
    decim = max(1, int(fs / target_if))
    if decim > 1:
        iq = lowpass(iq, fs, target_if / 2 * 0.9)
        iq = iq[::decim]
        fs_if = fs / decim
    else:
        fs_if = fs
    print("IF rate %s (decim %d)" % (eng(fs_if, "Hz"), decim))

    if a.mode == "am":
        audio = np.abs(iq)
        audio = audio - np.mean(audio)
    else:
        # FM discriminator
        audio = np.angle(iq[1:] * np.conj(iq[:-1]))

    audio = lowpass(audio, fs_if, aud_cut)

    if a.mode != "am" and a.deemph > 0:
        audio = deemphasis(audio, fs_if, a.deemph)

    audio = resample_to(audio, fs_if, a.audio_rate)

    # normalize
    peak = np.max(np.abs(audio)) + 1e-9
    audio = (audio / peak * 0.9 * 32767).astype(np.int16)

    with wave.open(a.out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(a.audio_rate)
        w.writeframes(audio.tobytes())
    print("wrote %s (%s, %.1f s of audio at %d Hz)" %
          (a.out, a.mode, len(audio) / a.audio_rate, a.audio_rate))
    if not have_scipy():
        print("note: scipy not found; used numpy fallback filters (slower, lower quality)")


if __name__ == "__main__":
    main()
