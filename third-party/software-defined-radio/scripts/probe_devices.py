#!/usr/bin/env python3
"""Enumerate attached SDR devices by calling whatever vendor CLIs are installed.
Runs each tool if present and summarizes what was found. Never fails if a tool is missing.

Usage:
  python probe_devices.py
  python probe_devices.py --verbose
"""
import argparse
import shutil
import subprocess
import sys


CHECKS = [
    # (label, executable, args, short-timeout)
    ("RTL-SDR", "rtl_test", ["-t"], 4),
    ("HackRF", "hackrf_info", [], 6),
    ("Airspy", "airspy_info", [], 6),
    ("AirspyHF", "airspyhf_info", [], 6),
    ("SoapySDR (all)", "SoapySDRUtil", ["--find"], 10),
    ("USRP", "uhd_find_devices", [], 10),
    ("LimeSDR", "LimeUtil", ["--find"], 8),
    ("BladeRF", "bladeRF-cli", ["-p"], 8),
    ("PlutoSDR (usb)", "iio_info", ["-s"], 8),
]


def run(exe, args, timeout):
    try:
        cp = subprocess.run([exe] + args, capture_output=True, text=True, timeout=timeout)
        return cp.returncode, (cp.stdout or "") + (cp.stderr or "")
    except subprocess.TimeoutExpired:
        return None, "(timed out)"
    except Exception as e:
        return None, "(error: %s)" % e


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true", help="print full tool output")
    a = ap.parse_args()

    print("Scanning for SDR devices and tools...\n")
    found_any = False
    installed = []
    for label, exe, args, to in CHECKS:
        path = shutil.which(exe)
        if not path:
            print("  [ - ] %-16s tool '%s' not installed" % (label, exe))
            continue
        installed.append(exe)
        rc, out = run(exe, args, to)
        out_stripped = out.strip()
        # heuristic: did it actually find a device? Require a positive marker AND no negative one.
        low = out_stripped.lower()
        NEG = ("no supported devices", "no hackrf boards found", "not found", "no devices attached",
               "no uhd devices found", "no devices found", "not_found", "0 devices", "error_not_found",
               "no device", "no iio context", "unable to open", "failed")
        POS = ("serial:", "serial number", "board id", "part number", "part id", "found 1",
               "found device", "found: 1", "nuand", "usrp", "supported tuner", "product",
               "iio context has", "hackrf one")
        neg = any(m in low for m in NEG)
        pos = any(m in low for m in POS)
        device_seen = pos and not neg
        if device_seen:
            found_any = True
        print("  [%s] %-16s (%s)" % ("+++" if device_seen else "   ", label, exe))
        if a.verbose and out_stripped:
            for line in out_stripped.splitlines()[:25]:
                print("        | " + line)
        elif out_stripped:
            first = out_stripped.splitlines()[0][:80]
            print("        %s" % first)

    print()
    if not installed:
        print("No SDR command-line tools found on PATH.")
        print("Install at least: rtl-sdr (rtl_test), and SoapySDR (SoapySDRUtil).")
        print("See references/software-toolchain.md for install recipes.")
    elif not found_any:
        print("Tools are installed but no device was detected.")
        print("Check: USB cable/port, Windows driver (Zadig -> WinUSB), Linux udev + blacklist")
        print("dvb_usb_rtl28xxu, and that no other app holds the device.")
        print("See references/troubleshooting.md section 1.")
    else:
        print("At least one SDR device was detected. Use SoapySDRUtil --probe=\"driver=...\"")
        print("for full capabilities (gains, sample rates, antennas).")


if __name__ == "__main__":
    main()
