# GNU Radio Reference (3.10.x)

## 1. Concepts

- A **flowgraph** is a directed graph of blocks; the scheduler moves buffers of **items**
  between them. Item types: complex float32 (`cf32`, blue), float32 (orange), int32, int16
  (`short`, yellow), int8 (`byte`, purple), message ports (grey, dashed).
- **Sample rate is not a property of the graph**; it is whatever each block assumes. You
  track it yourself. Every filter/demod block has a `samp_rate` or similar parameter that must
  equal the actual rate at its input, and decimating blocks divide it.
- Block kinds: sync (1:1), decimator (N:1), interpolator (1:N), general (variable), hier
  (contains a subgraph), tagged-stream (packet-length tagged), message-passing (PDU).
- **Stream tags** carry metadata with samples (`rx_time`, `rx_rate`, `rx_freq`, `packet_len`).
- **Messages/PDUs** (`pmt` pairs of dict + u8vector) carry packets between blocks without a
  sample clock: `Correlate Access Code - Tag` -> `Tagged Stream to PDU` -> `PDU to ...`.
- **Throttle**: rate limiter for graphs with no hardware clock. One per graph maximum, never
  with a hardware source/sink.
- GRC generates Python (`top_block.py`); you can run it headless with `--no-gui` options via
  the `Options` block (`Generate Options: No GUI`).

## 2. Essential blocks by category

| Category | Blocks (3.10 names) | Notes |
|---|---|---|
| Sources | `Soapy Custom/RTLSDR/HackRF/Airspy/... Source`, `UHD: USRP Source`, `IIO: PlutoSDR Source`, `osmocom Source` (gr-osmosdr), `File Source` (repeat, offset), `Signal Source`, `Noise Source`, `Vector Source`, `ZMQ SUB Source`, `UDP Source`, `Audio Source`, `Wav File Source` | Prefer native Soapy/UHD/IIO over osmocom |
| Sinks | `QT GUI Frequency/Waterfall/Time/Constellation Sink`, `QT GUI Sink` (all in one), `File Sink`, `File Meta Sink` (with tags), `Audio Sink`, `Wav File Sink`, `Null Sink`, `ZMQ PUB Sink`, `UDP Sink`, `Soapy/UHD/IIO Sink` (TX) | GUI sinks eat CPU; decimate first |
| Filters | `Low Pass Filter`, `Band Pass Filter`, `High Pass`, `Root Raised Cosine Filter`, `FIR Filter`, `IIR Filter`, `Frequency Xlating FIR Filter`, `Polyphase Channelizer`, `PFB Arbitrary Resampler`, `Rational Resampler`, `Decimating FIR Filter`, `DC Blocker`, `FFT Filter` (fast for long taps), `Single Pole IIR` | Taps via `firdes.low_pass(gain, fs, cutoff, transition, window)` |
| Math / type | `Multiply`, `Multiply Const`, `Add`, `Complex to Mag`, `Complex to Mag^2`, `Complex to Arg`, `Complex to Float`, `Float to Complex`, `Complex Conjugate`, `Delay`, `Log10`, `Abs`, `Threshold`, `Keep 1 in N`, `Keep M in N`, `Stream to Vector`, `Vector to Stream`, `Interleave`, `Deinterleave`, `Char to Float`, `Float to Char`, `Short to Float` | |
| Analog demod | `Quadrature Demod` (gain = fs/(2 pi dev)), `WBFM Receive`, `WBFM Receive PLL`, `NBFM Receive`, `AM Demod`, `PLL Freq Det`, `PLL Carrier Tracking`, `Costas Loop`, `AGC`, `AGC2`, `AGC3`, `Simple Squelch`, `Power Squelch`, `Standard Squelch`, `Feed Forward AGC`, `FM Deemphasis` | |
| Digital | `Symbol Sync` (replaces Clock Recovery MM / Polyphase Clock Sync), `Costas Loop`, `FLL Band-Edge`, `Constellation Decoder`, `Constellation Soft Decoder`, `Constellation Object`, `Differential Decoder/Encoder`, `Binary Slicer`, `Correlate Access Code (- Tag / - Tag Stream)`, `Packet Header Parser/Generator`, `Chunks to Symbols`, `Pack/Unpack K Bits`, `Descrambler`, `Additive Scrambler`, `CMA Equalizer`, `LMS DD Equalizer`, `Linear Equalizer`, `OFDM Receiver/Transmitter` hier blocks, `GFSK/GMSK/PSK/QAM Mod/Demod` hier blocks, `Map`, `Repack Bits`, `Crc32`, `CRC Append/Check`, `FEC Encoder/Decoder` (conv, LDPC, polar, repetition, dummy) | |
| Packet / PDU | `PDU to Tagged Stream`, `Tagged Stream to PDU`, `Message Debug`, `Message Strobe`, `PDU Set`, `PDU Filter`, `Random PDU Generator`, `Socket PDU` (TCP/UDP), `Protocol Formatter`, `Protocol Parser`, `Tag Debug`, `Stream to Tagged Stream`, `Tagged Stream Mux`, `Tagged Stream Align` | |
| Control | `Variable`, `QT GUI Range/Chooser/Check Box/Entry/Push Button/Tab Widget`, `Function Probe`, `Probe Signal`, `Probe Avg Mag^2`, `Head` (stop after N), `Skip Head`, `Selector`, `Mute`, `Copy` | Use `QT GUI Range` for tuning knobs |
| Custom | `Python Block` (embedded), `Python Module`, `Python Snippet`, OOT module blocks | |

## 3. Canonical flowgraphs (Python form)

### 3.1 WBFM receiver (RTL-SDR via Soapy)

```python
#!/usr/bin/env python3
from gnuradio import gr, analog, filter, audio, soapy
from gnuradio.filter import firdes

class wbfm_rx(gr.top_block):
    def __init__(self, freq=100.1e6, samp_rate=2.4e6, gain=30):
        super().__init__("wbfm_rx")
        quad_rate, audio_rate = 240e3, 48e3
        src = soapy.source("driver=rtlsdr", "fc32", 1, "", "", [""], [""])
        src.set_sample_rate(0, samp_rate)
        src.set_frequency(0, freq)
        src.set_gain_mode(0, False)
        src.set_gain(0, "TUNER", gain)
        chan = filter.freq_xlating_fir_filter_ccf(
            int(samp_rate / quad_rate),
            firdes.low_pass(1.0, samp_rate, 100e3, 20e3, firdes.WIN_HAMMING),
            0.0, samp_rate)                                   # 2.4 M -> 240 k
        demod = analog.wfm_rcv(quad_rate=quad_rate, audio_decimation=int(quad_rate / audio_rate))
        snk = audio.sink(int(audio_rate), "", True)
        self.connect(src, chan, demod, snk)

if __name__ == "__main__":
    tb = wbfm_rx(); tb.start(); input("running, Enter to stop\n"); tb.stop(); tb.wait()
```

### 3.2 NBFM channel with squelch (from a wideband file)

```
File Source (cf32, repeat) -> Throttle(samp_rate) -> Frequency Xlating FIR (decim 10, taps LPF 8 kHz, center f_off)
 -> Power Squelch (-50 dB) -> NBFM Receive (quad_rate 240k? no: use 48k*4=192k -> use decim so rate=192k; audio 48k)
 -> Audio Sink 48k
```
Rate bookkeeping: 2.4 M / 10 = 240 k; NBFM Receive wants `quad_rate` a multiple of `audio_rate`:
use Rational Resampler 240 k -> 192 k (up 4, down 5), then `NBFM Receive(audio_rate=48k, quad_rate=192k)`.

### 3.3 FSK/GFSK packet receiver (e.g. 433 MHz sensor, 38.4 kbaud, dev 20 kHz)

```
Source (fs = 1 M) -> Freq Xlating FIR (decim 5 -> 200 k, LPF 60 kHz, center f_off)
 -> Quadrature Demod (gain = 200e3/(2*pi*20e3))
 -> Low Pass (cutoff 30 k, transition 10 k)
 -> Symbol Sync (TED: Gardner or Mueller&Muller, sps = 200e3/38.4e3 = 5.208, loop bw 0.045, max dev 1.5)
 -> Binary Slicer
 -> Correlate Access Code - Tag Stream (access code "1010101010101010 + sync word bits", threshold 2, len)
 -> Repack Bits (1->8) -> Tagged Stream to PDU -> Message Debug / Socket PDU
```
DC offset in the demod output (frequency error) shifts the slicer threshold: add a `DC Blocker`
or a `Single Pole IIR` subtractor before the slicer, or use the burst-mean trick in a Python block.

### 3.4 BPSK/QPSK receiver (satellite-style, R_s = 72 kbaud)

```
Source (fs = 1.024 M) -> Freq Xlating FIR (decim 4 -> 256 k, LPF 60 k)
 -> AGC2 (attack 1e-3, decay 1e-4, ref 1)
 -> FLL Band-Edge (sps 3.556, rolloff 0.6, filter size 55, bw 2pi/200)     # coarse freq
 -> Polyphase or Symbol Sync (sps = 256e3/72e3 = 3.556, RRC taps alpha 0.6, nfilts 32, loop bw 2pi/100)
 -> Costas Loop (order 4 for QPSK, bw 2pi/100)
 -> Constellation Decoder (QPSK constellation object) -> Differential Decoder (if needed)
 -> Unpack K Bits / Map -> Correlate Access Code (sync word) -> frame handling (or gr-satellites)
```

### 3.5 Transmit GFSK burst (lab, cabled)

```
Vector Source (bytes, repeat off) or PDU -> Packet Header + payload -> GFSK Mod (sps 8, BT 0.5, sensitivity = 2*pi*dev/fs)
 -> Multiply Const (0.5) -> Soapy/UHD/IIO Sink (fs = sps*R_s * interp)
```
Keep peak |x| <= 0.7 to avoid DAC clipping; apply an `Interpolating FIR` to reach the device
rate if `sps*R_s` is below the device minimum (HackRF >= 2 MS/s).

## 4. Parameter formulas you keep needing

- `Quadrature Demod` gain: `fs / (2*pi*deviation)` -> output in units of "1.0 = full deviation".
- `Symbol Sync` sps: `fs / R_s` (can be fractional); loop bandwidth `2*pi/100` to `2*pi/400`;
  damping 1.0; max deviation 1.5; output sps 1 (or 2 for decision-directed equalizers).
- `Costas Loop` bw: `2*pi/100`; order 2 (BPSK), 4 (QPSK), 8 (8PSK).
- RRC taps: `firdes.root_raised_cosine(gain=nfilts, sampling_freq=nfilts*fs, symbol_rate=R_s, alpha, ntaps=11*sps*nfilts)`.
- Low-pass taps: `firdes.low_pass(1, fs, cutoff, transition_width, window.WIN_HAMMING)`;
  transition width of ~10-20 % of cutoff keeps taps reasonable.
- `Frequency Xlating FIR` center frequency = signal offset from `fc` (positive = above); decimation
  must give an output rate the next block expects.
- `WBFM Receive`: `quad_rate` (input rate) and `audio_decimation` (quad_rate/audio_rate must be integer).
- `NBFM Receive`: `audio_rate`, `quad_rate` (multiple of audio rate), `tau` 75e-6, `max_dev` 5e3.
- Power Squelch threshold in dB relative to full scale; `Simple Squelch` in dB after AGC.

## 5. Embedded Python block skeleton

```python
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    """Burst-normalize magnitude: divides each sample by a running max."""
    def __init__(self, alpha=0.01):
        gr.sync_block.__init__(self, name="burst_norm", in_sig=[np.complex64], out_sig=[np.complex64])
        self.alpha = alpha
        self.peak = 1e-3
    def work(self, input_items, output_items):
        x = input_items[0]
        mag = np.abs(x)
        for i in range(len(x)):
            self.peak = max(mag[i], self.peak * (1 - self.alpha))
            output_items[0][i] = x[i] / (self.peak + 1e-9)
        return len(output_items[0])
```
Use `gr.decim_block` / `gr.interp_block` / `gr.basic_block` for other ratios; message ports via
`self.message_port_register_in(pmt.intern("in")); self.set_msg_handler(pmt.intern("in"), self.handle)`.

## 6. OOT modules

```bash
gr_modtool newmod mymod && cd gr-mymod
gr_modtool add -t sync -l python my_block      # or -l cpp
# edit python/mymod/my_block.py and grc/mymod_my_block.block.yml
mkdir build && cd build && cmake .. && make -j && sudo make install && sudo ldconfig
```
Common OOT modules: gr-osmosdr, gr-satellites, gr-lora_sdr, gr-gsm, gr-ieee802-11, gr-ieee802-15-4,
gr-rds, gr-dab, gr-iridium, gr-adsb, gr-ais, gr-fosphor, gr-inspector, gr-radar, gr-paint, gr-dvbs2rx,
gr-op25, gr-limesdr, gr-iio (built into 3.10). Check the module's README for the GNU Radio version it targets.

## 7. Performance and debugging

- Console `O` = overflow at the source (host too slow to pull samples), `U` = underflow at the sink
  (host too slow to feed TX), `D` = dropped packets (UHD network), `S` = sequence error.
  Fixes: lower `fs`, decimate right after the source, remove GUI sinks or lower their FFT size and
  update rate, set `GR_SCHEDULER=TPB` (default), raise `output buffer` sizes, use `FFT Filter` for
  long taps, pin CPU governor to performance, use a USB3 port and short cable.
- VOLK: run `volk_profile` once so kernels use SIMD.
- `gr-inspector`, `Tag Debug`, `Message Debug`, `Probe` blocks and `QT GUI Time Sink` with trigger on
  tag are your oscilloscope.
- Latency: bigger buffers = more latency; for TX bursts use `tx_time`/`tx_sob`/`tx_eob` tags (UHD)
  or PDU-based bursts with `Tagged Stream` sinks.
- Headless: generate with `No GUI`, run `python3 top_block.py`; use `Function Probe` + Python to
  script parameter changes, or ZMQ/XML-RPC (`XMLRPC Server` block) for remote control.
- Recording with metadata: `File Meta Sink` (GNU Radio metadata) or record `File Sink` cf32 and write
  a SigMF meta file (`scripts/sigmf_write.py`).

## 8. Migration notes

- 3.7 -> 3.8: Python 3, `WX GUI` removed, `gr-analog`/`gr-digital` reorganizations.
- 3.8 -> 3.9/3.10: `Clock Recovery MM` and `Polyphase Clock Sync` still exist but `Symbol Sync`
  is the recommended block; `firdes.WIN_*` moved to `fft.window.WIN_*`; native `Soapy`, `IIO`, `UHD`
  blocks; `pdu` blocks moved to `gr-pdu` (`blocks.pdu_to_tagged_stream` -> `pdu.pdu_to_tagged_stream`);
  `gr-osmosdr` still works for 3.10.
- 3.10 -> 3.11/4.0: new runtime and scheduler; expect block/yaml changes; older OOT modules need porting.
