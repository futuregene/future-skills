#!/usr/bin/env python3
"""Write a SigMF metadata (.sigmf-meta) file for an existing IQ capture, and optionally
copy/convert the data to a .sigmf-data file. No external dependencies (plain JSON).

Examples:
  python sigmf_write.py cap.cs16 --fs 4e6 --fc 1090e6 --hw "HackRF One"
  python sigmf_write.py cap.cu8 --fs 2.4e6 --fc 433.92e6 --hw "RTL-SDR V4" --datatype cu8 --meta-only
  python sigmf_write.py cap.cf32 --fs 8M --fc 915M --hw "Airspy" --author me --desc "ISM survey"

By default it produces <name>.sigmf-meta beside the data file and sets core:datatype from the
file extension. Use --datatype to force it. SigMF datatypes: cf32_le, ci16_le, ci8, cu8, cf64_le.
"""
import argparse
import datetime as dt
import json
import os
import sys

try:
    from _common import guess_format, parse_freq, file_num_complex, FORMATS
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _common import guess_format, parse_freq, file_num_complex, FORMATS

# map our internal format to a SigMF datatype string
FMT_TO_SIGMF = {
    "cu8": "cu8",
    "cs8": "ci8",
    "cs16": "ci16_le",
    "cf32": "cf32_le",
    "cf64": "cf64_le",
}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="existing IQ capture")
    p.add_argument("--fs", required=True, help="sample rate (Hz or 2.4M)")
    p.add_argument("--fc", required=True, help="center frequency (Hz or 433.92M)")
    p.add_argument("--hw", default="", help="hardware description (e.g. 'RTL-SDR Blog V4')")
    p.add_argument("--author", default="")
    p.add_argument("--desc", default="")
    p.add_argument("--datatype", default=None, help="override SigMF datatype string")
    p.add_argument("--format", default=None, help="input format if extension is ambiguous")
    p.add_argument("--datetime", default=None, help="ISO8601 UTC; default now")
    p.add_argument("--meta-only", action="store_true",
                   help="write only .sigmf-meta next to the existing file (do not rename data)")
    a = p.parse_args()

    infmt = guess_format(a.file, a.format)
    if infmt is None:
        print("cannot infer format; pass --format or --datatype"); sys.exit(2)
    datatype = a.datatype or FMT_TO_SIGMF.get(infmt, "cf32_le")

    fs = parse_freq(a.fs)
    fc = parse_freq(a.fc)
    when = a.datetime or (dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    base = os.path.splitext(a.file)[0]
    if a.meta_only:
        meta_path = base + ".sigmf-meta"
        data_ref = os.path.basename(a.file)
    else:
        data_path = base + ".sigmf-data"
        if os.path.abspath(data_path) != os.path.abspath(a.file):
            # copy bytes verbatim (datatype must match the actual bytes)
            with open(a.file, "rb") as fi, open(data_path, "wb") as fo:
                while True:
                    chunk = fi.read(1 << 20)
                    if not chunk:
                        break
                    fo.write(chunk)
        meta_path = base + ".sigmf-meta"
        data_ref = os.path.basename(data_path)

    n_complex = file_num_complex(a.file, infmt)

    meta = {
        "global": {
            "core:datatype": datatype,
            "core:sample_rate": float(fs),
            "core:version": "1.2.0",
            "core:num_channels": 1,
        },
        "captures": [
            {
                "core:sample_start": 0,
                "core:frequency": float(fc),
                "core:datetime": when,
            }
        ],
        "annotations": [],
    }
    if a.hw:
        meta["global"]["core:hw"] = a.hw
    if a.author:
        meta["global"]["core:author"] = a.author
    if a.desc:
        meta["global"]["core:description"] = a.desc

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")

    print("wrote %s" % meta_path)
    print("  datatype    : %s" % datatype)
    print("  sample_rate : %g Hz" % fs)
    print("  frequency   : %g Hz" % fc)
    print("  datetime    : %s" % when)
    print("  samples     : %s complex (%.2f s)" % (f"{n_complex:,}", n_complex / fs))
    print("  data file   : %s" % data_ref)
    print("\nNote: core:datatype must match the actual bytes. If your file is not %s,"
          " pass --datatype." % datatype)


if __name__ == "__main__":
    main()
