#!/usr/bin/env python3
"""SDR calculators: wavelength, dipole, dBm/W/uV, noise floor, FSPL, link budget,
Friis NF, Carson BW, FFT resolution, Doppler, file size, symbol-rate<->BW.

Examples:
  python sdr_calc.py wavelength --f-mhz 433.92
  python sdr_calc.py dipole --f-mhz 137.5
  python sdr_calc.py fspl --d-km 200 --f-mhz 1090
  python sdr_calc.py noise --bw 2e6 --nf 6
  python sdr_calc.py link --ptx 20 --gtx 2 --grx 2 --d-km 10 --f-mhz 915
  python sdr_calc.py dbm --dbm -50
  python sdr_calc.py friis --nf 1 0.8 6 --gain 20 20
  python sdr_calc.py carson --dev 75e3 --fm 15e3
  python sdr_calc.py fft --fs 2.4e6 --nfft 4096
  python sdr_calc.py doppler --f-mhz 137 --v 7.5e3
  python sdr_calc.py filesize --fs 2.4e6 --sec 30 --fmt cu8
  python sdr_calc.py symbolbw --rs 72e3 --alpha 0.35
"""
import argparse
import math
import sys

try:
    from _common import parse_freq, eng
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import parse_freq, eng

C = 299_792_458.0
BYTES = {"cu8": 2, "cs8": 2, "cs16": 4, "cf32": 8, "cf64": 16}


def w_from_dbm(dbm):
    return 10 ** ((dbm - 30) / 10)


def dbm_from_w(w):
    return 10 * math.log10(w * 1000)


def cmd_wavelength(a):
    f = parse_freq(a.f_mhz) * 1e6
    lam = C / f
    print("f = %s" % eng(f, "Hz"))
    print("wavelength   = %.4f m  (%.2f cm)" % (lam, lam * 100))
    print("half wave    = %.4f m" % (lam / 2))
    print("quarter wave = %.4f m" % (lam / 4))


def cmd_dipole(a):
    fmhz = parse_freq(a.f_mhz) / 1e6 if parse_freq(a.f_mhz) > 1e5 else parse_freq(a.f_mhz)
    # accept MHz directly
    fmhz = parse_freq(a.f_mhz)
    if fmhz > 1e5:
        fmhz = fmhz / 1e6
    total = 143.0 / fmhz
    leg = 71.5 / fmhz
    print("f = %.4f MHz" % fmhz)
    print("half-wave dipole total length = %.3f m  (%.1f cm), each leg %.3f m (%.1f cm)"
          % (total, total * 100, leg, leg * 100))
    print("quarter-wave vertical         = %.3f m  (%.1f cm)" % (leg, leg * 100))
    print("NOAA-style V-dipole (137 MHz uses ~53.4 cm legs at 120 deg)")


def cmd_fspl(a):
    d = a.d_km
    fmhz = parse_freq(a.f_mhz)
    if fmhz > 1e5:
        fmhz = fmhz / 1e6
    loss = 20 * math.log10(d) + 20 * math.log10(fmhz) + 32.44
    print("Free-space path loss at d=%g km, f=%g MHz:" % (d, fmhz))
    print("  FSPL = %.2f dB" % loss)


def cmd_noise(a):
    bw = parse_freq(a.bw)
    nf = a.nf
    n = -174 + 10 * math.log10(bw) + nf
    print("Thermal noise floor:")
    print("  BW = %s, NF = %.1f dB" % (eng(bw, "Hz"), nf))
    print("  N = -174 + 10log10(BW) + NF = %.2f dBm" % n)
    if a.snr is not None:
        print("  Sensitivity for %.1f dB SNR = %.2f dBm" % (a.snr, n + a.snr))


def cmd_link(a):
    fmhz = parse_freq(a.f_mhz)
    if fmhz > 1e5:
        fmhz = fmhz / 1e6
    fspl = 20 * math.log10(a.d_km) + 20 * math.log10(fmhz) + 32.44
    prx = a.ptx + a.gtx - fspl - a.lcable + a.grx
    print("Link budget:")
    print("  Ptx %.1f dBm + Gtx %.1f dBi - FSPL %.2f dB - cable %.1f dB + Grx %.1f dBi"
          % (a.ptx, a.gtx, fspl, a.lcable, a.grx))
    print("  Prx = %.2f dBm" % prx)
    if a.bw and a.nf is not None:
        n = -174 + 10 * math.log10(parse_freq(a.bw)) + a.nf
        print("  Noise floor (BW %s, NF %.1f) = %.2f dBm -> SNR = %.1f dB"
              % (eng(parse_freq(a.bw), "Hz"), a.nf, n, prx - n))


def cmd_dbm(a):
    if a.dbm is not None:
        w = w_from_dbm(a.dbm)
        vrms = math.sqrt(w * 50)
        print("%.2f dBm = %s W = %s V rms (50 ohm) = %s Vpp"
              % (a.dbm, eng(w, "W"), eng(vrms, "V"), eng(vrms * 2 * math.sqrt(2), "V")))
    elif a.w is not None:
        print("%s W = %.2f dBm" % (eng(a.w, "W"), dbm_from_w(a.w)))
    elif a.uv is not None:
        w = (a.uv * 1e-6) ** 2 / 50
        print("%g uV rms (50 ohm) = %.2f dBm" % (a.uv, dbm_from_w(w)))
    else:
        print("give --dbm, --w, or --uv")


def cmd_friis(a):
    nfs = a.nf
    gains = a.gain
    if len(gains) < len(nfs) - 1:
        print("need at least len(nf)-1 gains")
        return
    f = 10 ** (nfs[0] / 10)
    gcum = 1.0
    for i in range(1, len(nfs)):
        gcum *= 10 ** (gains[i - 1] / 10)
        f += (10 ** (nfs[i] / 10) - 1) / gcum
    print("Cascade noise figure:")
    print("  stages NF(dB) = %s, gains(dB) = %s" % (nfs, gains))
    print("  total NF = %.3f dB (F = %.4f linear)" % (10 * math.log10(f), f))


def cmd_carson(a):
    dev = parse_freq(a.dev)
    fm = parse_freq(a.fm)
    bw = 2 * (dev + fm)
    print("Carson bandwidth = 2*(dev + f_m) = %s" % eng(bw, "Hz"))
    print("  deviation %s, max audio %s, mod index = %.2f" % (eng(dev, "Hz"), eng(fm, "Hz"), dev / fm))


def cmd_fft(a):
    fs = parse_freq(a.fs)
    n = a.nfft
    print("FFT resolution:")
    print("  fs = %s, N = %d" % (eng(fs, "Hz"), n))
    print("  bin spacing df = fs/N = %s" % eng(fs / n, "Hz"))
    print("  frame time = N/fs = %s" % eng(n / fs, "s"))


def cmd_doppler(a):
    fmhz = parse_freq(a.f_mhz)
    f = fmhz * 1e6 if fmhz < 1e5 else fmhz
    v = a.v
    shift = f * v / C
    print("Doppler at f=%s, radial velocity %g m/s:" % (eng(f, "Hz"), v))
    print("  max shift = f*v/c = +-%s" % eng(shift, "Hz"))


def cmd_filesize(a):
    fs = parse_freq(a.fs)
    sec = a.sec
    bps = BYTES[a.fmt]
    total = fs * sec * bps
    print("Recording size:")
    print("  fs=%s, %g s, %s (%d bytes/complex sample)" % (eng(fs, "Hz"), sec, a.fmt, bps))
    print("  size = %s (%.1f MB), rate = %s/s" % (eng(total, "B"), total / 1e6, eng(fs * bps, "B")))


def cmd_symbolbw(a):
    if a.rs and a.alpha is not None:
        rs = parse_freq(a.rs)
        bw = rs * (1 + a.alpha)
        print("RRC occupied BW = Rs*(1+alpha) = %s (Rs=%s, alpha=%.2f)"
              % (eng(bw, "Hz"), eng(rs, "Hz"), a.alpha))
    elif a.bw and a.alpha is not None:
        bw = parse_freq(a.bw)
        rs = bw / (1 + a.alpha)
        print("Symbol rate = BW/(1+alpha) = %s (BW=%s, alpha=%.2f)"
              % (eng(rs, "Hz"), eng(bw, "Hz"), a.alpha))
    else:
        print("give --rs (+ --alpha) or --bw (+ --alpha)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("wavelength"); s.add_argument("--f-mhz", required=True); s.set_defaults(fn=cmd_wavelength)
    s = sub.add_parser("dipole"); s.add_argument("--f-mhz", required=True); s.set_defaults(fn=cmd_dipole)
    s = sub.add_parser("fspl"); s.add_argument("--d-km", type=float, required=True); s.add_argument("--f-mhz", required=True); s.set_defaults(fn=cmd_fspl)
    s = sub.add_parser("noise"); s.add_argument("--bw", required=True); s.add_argument("--nf", type=float, default=6.0); s.add_argument("--snr", type=float); s.set_defaults(fn=cmd_noise)
    s = sub.add_parser("link"); s.add_argument("--ptx", type=float, required=True); s.add_argument("--gtx", type=float, default=0); s.add_argument("--grx", type=float, default=0); s.add_argument("--lcable", type=float, default=0); s.add_argument("--d-km", type=float, required=True); s.add_argument("--f-mhz", required=True); s.add_argument("--bw"); s.add_argument("--nf", type=float); s.set_defaults(fn=cmd_link)
    s = sub.add_parser("dbm"); s.add_argument("--dbm", type=float); s.add_argument("--w", type=float); s.add_argument("--uv", type=float); s.set_defaults(fn=cmd_dbm)
    s = sub.add_parser("friis"); s.add_argument("--nf", type=float, nargs="+", required=True); s.add_argument("--gain", type=float, nargs="+", required=True); s.set_defaults(fn=cmd_friis)
    s = sub.add_parser("carson"); s.add_argument("--dev", required=True); s.add_argument("--fm", required=True); s.set_defaults(fn=cmd_carson)
    s = sub.add_parser("fft"); s.add_argument("--fs", required=True); s.add_argument("--nfft", type=int, default=4096); s.set_defaults(fn=cmd_fft)
    s = sub.add_parser("doppler"); s.add_argument("--f-mhz", required=True); s.add_argument("--v", type=float, default=7.5e3); s.set_defaults(fn=cmd_doppler)
    s = sub.add_parser("filesize"); s.add_argument("--fs", required=True); s.add_argument("--sec", type=float, required=True); s.add_argument("--fmt", default="cu8", choices=list(BYTES)); s.set_defaults(fn=cmd_filesize)
    s = sub.add_parser("symbolbw"); s.add_argument("--rs"); s.add_argument("--bw"); s.add_argument("--alpha", type=float, default=0.35); s.set_defaults(fn=cmd_symbolbw)

    a = p.parse_args()
    if not getattr(a, "cmd", None):
        p.print_help()
        return
    a.fn(a)


if __name__ == "__main__":
    main()
