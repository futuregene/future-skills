#!/usr/bin/env python3
"""Broadcast WBFM receiver flowgraph (GNU Radio 3.10, no GUI).

Chain: Soapy source -> Frequency Xlating FIR (channelize + decimate) -> WBFM demod -> audio.

Run:
  python gr_wbfm_rx.py --freq 100.1e6 --gain 30 --driver rtlsdr
  python gr_wbfm_rx.py --freq 94.7e6 --driver hackrf --samp-rate 8e6

Change --driver to hackrf, airspy, sdrplay, bladerf, plutosdr, uhd (each needs its Soapy module).
This is a hand-written flowgraph you can also rebuild visually in gnuradio-companion.
"""
import argparse
import signal
import sys
import time

try:
    from gnuradio import gr, analog, filter, audio, soapy
    from gnuradio.filter import firdes
except ImportError:
    sys.stderr.write("GNU Radio 3.10 with the Soapy blocks is required. "
                     "See references/software-toolchain.md.\n")
    sys.exit(1)


class wbfm_rx(gr.top_block):
    def __init__(self, driver="rtlsdr", freq=100.1e6, samp_rate=2.4e6, gain=30,
                 audio_rate=48000, offset=0.0):
        gr.top_block.__init__(self, "WBFM RX")
        quad_rate = 240000
        decim = int(round(samp_rate / quad_rate))
        audio_decim = int(round(quad_rate / audio_rate))

        self.src = soapy.source("driver=" + driver, "fc32", 1, "", "", [""], [""])
        self.src.set_sample_rate(0, samp_rate)
        self.src.set_frequency(0, freq)
        self.src.set_gain_mode(0, False)
        try:
            self.src.set_gain(0, gain)
        except Exception:
            self.src.set_gain(0, "TUNER", gain)

        # channel filter: low-pass ~100 kHz, translate 'offset' to 0, decimate to quad_rate
        taps = firdes.low_pass(1.0, samp_rate, 100e3, 20e3, fft_window_ok())
        self.chan = filter.freq_xlating_fir_filter_ccc(decim, taps, offset, samp_rate)

        self.demod = analog.wfm_rcv(quad_rate=quad_rate, audio_decimation=audio_decim)
        self.sink = audio.sink(audio_rate, "", True)

        self.connect(self.src, self.chan, self.demod, self.sink)


def fft_window_ok():
    # firdes window enum moved between versions; be tolerant
    try:
        from gnuradio.fft import window
        return window.WIN_HAMMING
    except Exception:
        return firdes.WIN_HAMMING


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--driver", default="rtlsdr")
    ap.add_argument("--freq", type=float, default=100.1e6)
    ap.add_argument("--samp-rate", type=float, default=2.4e6)
    ap.add_argument("--gain", type=float, default=30)
    ap.add_argument("--audio-rate", type=int, default=48000)
    ap.add_argument("--offset", type=float, default=0.0,
                    help="tune fc off-signal by this and set offset to avoid the DC spike")
    a = ap.parse_args()

    tb = wbfm_rx(a.driver, a.freq, a.samp_rate, a.gain, a.audio_rate, a.offset)
    tb.start()
    print("WBFM RX running: %.4f MHz via %s. Ctrl-C to stop." % (a.freq / 1e6, a.driver))
    def stop(*_):
        tb.stop(); tb.wait(); sys.exit(0)
    signal.signal(signal.SIGINT, stop)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop()


if __name__ == "__main__":
    main()
