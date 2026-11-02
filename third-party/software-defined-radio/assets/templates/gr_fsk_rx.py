#!/usr/bin/env python3
"""Generic 2-FSK / GFSK packet receiver to a bitstream (GNU Radio 3.10, no GUI).

Chain: source (or file) -> xlating FIR (channelize+decimate) -> quad demod -> LPF ->
Symbol Sync -> binary slicer -> correlate access code -> PDU -> printed hex.

Tune the four numbers for your signal: --rate (symbol rate), --dev (deviation),
--offset (signal offset from center), and --access (sync word bits).

Run on live hardware:
  python gr_fsk_rx.py --driver rtlsdr --freq 433.92e6 --samp-rate 1e6 --rate 38400 --dev 20000
Run on a recorded file (cf32):
  python gr_fsk_rx.py --file cap.cf32 --samp-rate 1e6 --rate 38400 --dev 20000 --offset 0

This is a starting point; real devices need the right access code, whitening, and CRC.
For unknown signals, reverse-engineer in Universal Radio Hacker first.
"""
import argparse
import math
import sys
import time

try:
    from gnuradio import gr, analog, filter, blocks, digital, soapy, pdu
    from gnuradio.filter import firdes
    import pmt
except ImportError:
    sys.stderr.write("GNU Radio 3.10 (with soapy, digital, pdu) required.\n")
    sys.exit(1)


def win():
    try:
        from gnuradio.fft import window
        return window.WIN_HAMMING
    except Exception:
        return firdes.WIN_HAMMING


class fsk_rx(gr.top_block):
    def __init__(self, source_args):
        gr.top_block.__init__(self, "FSK RX")
        a = source_args
        samp_rate = a.samp_rate
        if_rate = 200000.0
        decim = max(1, int(round(samp_rate / if_rate)))
        if_rate = samp_rate / decim
        sps = if_rate / a.rate

        # source
        if a.file:
            fsrc = blocks.file_source(gr.sizeof_gr_complex, a.file, a.repeat)
            thr = blocks.throttle(gr.sizeof_gr_complex, samp_rate)
            head = fsrc
            self._pre = [fsrc, thr]
        else:
            src = soapy.source("driver=" + a.driver, "fc32", 1, "", "", [""], [""])
            src.set_sample_rate(0, samp_rate)
            src.set_frequency(0, a.freq)
            src.set_gain_mode(0, False)
            try:
                src.set_gain(0, a.gain)
            except Exception:
                src.set_gain(0, "TUNER", a.gain)
            self._pre = [src]

        taps = firdes.low_pass(1.0, samp_rate, a.dev * 1.5 + a.rate, a.rate * 0.5, win())
        chan = filter.freq_xlating_fir_filter_ccc(decim, taps, a.offset, samp_rate)
        quad = analog.quadrature_demod_cf(if_rate / (2 * math.pi * a.dev))
        lpf = filter.fir_filter_fff(1, firdes.low_pass(1.0, if_rate, a.rate, a.rate * 0.4, win()))

        # symbol sync (TED: Mueller & Muller works after the discriminator)
        ted = digital.symbol_sync_ff(
            digital.TED_MUELLER_AND_MULLER, sps, 0.045, 1.0, 1.0, 0.05, 1,
            digital.constellation_bpsk().base(), digital.IR_MMSE_8TAP, 128, [])
        slicer = digital.binary_slicer_fb()

        access = a.access.replace(" ", "")
        corr = digital.correlate_access_code_tag_bb(access, a.threshold, "pkt")
        # collect tagged stream to PDU after a fixed length
        t2p = pdu.tagged_stream_to_pdu(gr.types.byte_t, "pkt")
        self.dbg = blocks.message_debug()

        # connect
        prev = self._pre[0]
        for b in self._pre[1:]:
            self.connect(prev, b); prev = b
        self.connect(prev, chan, quad, lpf, ted, slicer, corr)
        # Note: producing clean PDUs needs a Packet Header/length; for a quick look,
        # print the sliced bits with a file sink instead:
        self.bits_sink = blocks.file_sink(gr.sizeof_char, a.bits_out, False) if a.bits_out else blocks.null_sink(gr.sizeof_char)
        self.connect(slicer, self.bits_sink)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--driver", default="rtlsdr")
    ap.add_argument("--file", default=None, help="cf32 IQ file instead of live source")
    ap.add_argument("--repeat", action="store_true")
    ap.add_argument("--freq", type=float, default=433.92e6)
    ap.add_argument("--samp-rate", type=float, default=1e6)
    ap.add_argument("--gain", type=float, default=30)
    ap.add_argument("--rate", type=float, default=38400, help="symbol rate (baud)")
    ap.add_argument("--dev", type=float, default=20000, help="FSK deviation (Hz)")
    ap.add_argument("--offset", type=float, default=0.0, help="signal offset from center (Hz)")
    ap.add_argument("--access", default="10101010101010101", help="access/sync code bits")
    ap.add_argument("--threshold", type=int, default=2, help="allowed access-code bit errors")
    ap.add_argument("--bits-out", default=None, help="write sliced bits (1 byte/bit) to this file")
    a = ap.parse_args()

    tb = fsk_rx(a)
    tb.start()
    print("FSK RX running (rate %g, dev %g). Ctrl-C to stop." % (a.rate, a.dev))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tb.stop(); tb.wait()


if __name__ == "__main__":
    main()
