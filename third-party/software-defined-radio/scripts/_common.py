"""Shared helpers for the SDR skill scripts. Pure numpy; no SDR hardware needed."""
import os
import sys
import numpy as np

# Sample formats: name -> (numpy dtype, bytes per complex sample, converter to unit-scale float)
FORMATS = {
    "cu8":  (np.uint8,   2),
    "cs8":  (np.int8,    2),
    "cs16": (np.int16,   4),
    "cf32": (np.float32, 8),
    "cf64": (np.float64, 16),
}
EXT_TO_FMT = {
    ".cu8": "cu8", ".u8": "cu8", ".rtl": "cu8",
    ".cs8": "cs8", ".s8": "cs8", ".c8": "cs8", ".int8": "cs8",
    ".cs16": "cs16", ".s16": "cs16", ".c16": "cs16", ".sc16": "cs16", ".int16": "cs16",
    ".cf32": "cf32", ".f32": "cf32", ".fc32": "cf32", ".complex64": "cf32", ".cfile": "cf32",
    ".cf64": "cf64", ".f64": "cf64", ".complex128": "cf64",
    ".sigmf-data": "cf32",
}


def parse_freq(s):
    """Accept 2.4e6, 2400000, '2.4M', '433.92M', '48k', '1.2G'."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().replace("_", "")
    mult = 1.0
    if s and s[-1] in "kKmMgGtT":
        mult = {"k": 1e3, "m": 1e6, "g": 1e9, "t": 1e12}[s[-1].lower()]
        s = s[:-1]
    return float(s) * mult


def guess_format(path, override=None):
    if override:
        return override
    lower = path.lower()
    for ext, fmt in EXT_TO_FMT.items():
        if lower.endswith(ext):
            return fmt
    return None


def read_iq(path, fmt=None, count=-1, start_sample=0):
    """Read interleaved IQ into complex64. start_sample and count are in COMPLEX samples."""
    fmt = guess_format(path, fmt)
    if fmt is None:
        raise ValueError(
            "Cannot determine sample format from extension; pass --format "
            "cu8|cs8|cs16|cf32|cf64"
        )
    dtype, bps = FORMATS[fmt]
    item = np.dtype(dtype).itemsize
    offset_bytes = start_sample * item * 2
    n_items = -1 if count < 0 else count * 2
    raw = np.fromfile(path, dtype=dtype, count=n_items, offset=offset_bytes)
    if raw.size % 2:
        raw = raw[:-1]
    raw = raw.astype(np.float32)
    if fmt == "cu8":
        raw = (raw - 127.5) / 127.5
    elif fmt == "cs8":
        raw = raw / 127.5
    elif fmt == "cs16":
        raw = raw / 32767.0
    iq = raw[0::2] + 1j * raw[1::2]
    return iq.astype(np.complex64), fmt


def write_iq(path, iq, fmt="cf32"):
    inter = np.empty(iq.size * 2, dtype=np.float32)
    inter[0::2] = iq.real
    inter[1::2] = iq.imag
    if fmt == "cf32":
        inter.astype(np.float32).tofile(path)
    elif fmt == "cf64":
        inter.astype(np.float64).tofile(path)
    elif fmt == "cu8":
        np.clip(inter * 127.5 + 127.5, 0, 255).astype(np.uint8).tofile(path)
    elif fmt == "cs8":
        np.clip(inter * 127.5, -128, 127).astype(np.int8).tofile(path)
    elif fmt == "cs16":
        np.clip(inter * 32767.0, -32768, 32767).astype(np.int16).tofile(path)
    else:
        raise ValueError("Unknown output format: %s" % fmt)


def file_num_complex(path, fmt):
    dtype, bps = FORMATS[fmt]
    return os.path.getsize(path) // bps


def eng(x, unit=""):
    """Engineering-notation formatter: 2400000 -> '2.400 M'."""
    if x == 0:
        return "0 " + unit
    from math import log10, floor
    prefixes = {-4: "p", -3: "n", -2: "u", -1: "m", 0: "", 1: "k", 2: "M", 3: "G", 4: "T"}
    exp = int(floor(log10(abs(x)) / 3))
    exp = max(-4, min(4, exp))
    return "%.3f %s%s" % (x / 10 ** (exp * 3), prefixes[exp], unit)


def have_scipy():
    try:
        import scipy.signal  # noqa
        return True
    except Exception:
        return False
