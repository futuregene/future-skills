# DSP Fundamentals for SDR

Everything here is written for complex-baseband (IQ) processing at a sample rate `fs`.
Formulas are stated once and then applied to concrete SDR numbers.

## 1. Sampling, Nyquist, and complex baseband

- **Real sampling**: a real ADC at rate `fs` represents frequencies `0 .. fs/2`. Anything
  above `fs/2` folds (aliases) back down. RTL-SDR direct-sampling mode is real sampling at
  28.8 MS/s, so HF up to 14.4 MHz is usable without an upconverter.
- **Complex (IQ) sampling**: the tuner mixes the RF band down so the tuned frequency `fc`
  becomes 0 Hz, producing two real streams I (in-phase) and Q (quadrature, 90 degrees
  shifted). Each complex sample `x = I + jQ`. A complex stream at rate `fs` represents
  `fc - fs/2 .. fc + fs/2`, i.e. a **span of `fs` Hz, not `fs/2`**. Negative frequencies
  are real, distinct frequencies below `fc`.
- **Why IQ**: a real signal cannot distinguish +f from -f; the quadrature channel makes
  the spectrum one-sided, so frequency shift, SSB, FM discrimination and phase tracking
  become simple complex arithmetic.
- **Analytic signal**: `x(t) = A(t) e^{j(2*pi*f t + phi(t))}`; `|x|` is instantaneous
  amplitude (AM info), `angle(x)` is instantaneous phase, `d/dt angle(x)` is instantaneous
  frequency (FM info).
- **Usable bandwidth** is less than `fs` because anti-alias filters roll off. Rules of
  thumb: RTL-SDR ~80 % of `fs`; HackRF ~75 % (its baseband filter is set to roughly 0.75 fs);
  Pluto/USRP set `rf_bandwidth` explicitly (commonly 0.8 fs).

## 2. Quantization, bits, and dynamic range

| ADC bits | Ideal SNR (6.02 N + 1.76 dB) | Real devices |
|---|---|---|
| 8 | 49.9 dB | RTL-SDR (~45 dB with dither), HackRF |
| 12 | 74 dB | Airspy, Pluto, LimeSDR, BladeRF, USRP B2x0 |
| 14 | 86 dB | SDRplay RSP |
| 16 | 98 dB | Some HF receivers, sound cards |

- **Processing gain**: averaging/filtering over N samples adds `10*log10(N)` dB of SNR
  for narrowband signals, which is why an 8-bit RTL-SDR can decode -120 dBm signals: the
  quantization noise spreads across the whole 2.4 MHz while the signal sits in 12.5 kHz
  (`10*log10(2.4e6/12.5e3) = 22.8 dB` of gain).
- **Clipping** is catastrophic and non-linear: it creates broadband splatter and images.
  Keep the peak 6-10 dB below full scale. Full scale: cu8 0/255, cs8 -128/127, cs16 depends
  on justification (Pluto uses 12 bits in the low bits; UHD sc16 uses the full 16 bits).
- **Dynamic range on a waterfall** is limited by the strongest signal in the span. A strong
  FM broadcast station in a 10 MHz span consumes the dynamic range for everything else.
  Narrow the span with a front-end filter, not just in software.

## 3. FFT, PSD, windowing, resolution

- Bin spacing `df = fs / N_FFT`. Time per frame `N_FFT / fs`. A 2.4 MS/s capture with
  N=4096 gives 586 Hz bins and 1.7 ms frames.
- **Window functions** trade main-lobe width for sidelobe leakage:
  Rectangular (sharpest, -13 dB sidelobes, use only for exact-bin tones),
  Hann (-31 dB, good default), Hamming (-43 dB), Blackman-Harris (-92 dB, use when a
  strong signal hides a weak neighbor, costs 2x resolution), Kaiser (tunable beta).
- **Welch PSD** (`scipy.signal.welch(x, fs, nperseg=N, return_onesided=False)`) averages
  overlapping windowed FFTs to reduce variance: the noise floor becomes flat and weak
  signals become visible. Use `np.fft.fftshift` to center 0 Hz.
- **Waterfall/spectrogram** = sequence of |FFT|^2 frames, log scale in dB. Frame overlap of
  50-75 % smooths bursts. For burst analysis use short frames (N=256-1024); for narrowband
  CW/FT8 use long frames (N=8192-65536).
- **dBFS vs dBm**: an SDR reports dB relative to full scale. Converting to dBm needs a
  calibrated reference; RTL-SDR gain figures are approximate, SDRplay and Airspy are closer.
- **Resolution bandwidth (RBW)** in spectrum-analyzer terms equals the window's equivalent
  noise bandwidth times `df`. The noise floor in a plot rises by `10*log10(RBW)`; always
  state RBW when comparing levels.

## 4. Filtering

**FIR** (finite impulse response): linear phase, always stable, more taps for sharp
transitions. Number of taps for a low-pass with transition width `tw` and attenuation
`A` dB (Kaiser estimate): `N ~= (A - 8) / (2.285 * 2*pi * tw/fs)`. Example: 60 dB, 100 kHz
transition at 2.4 MS/s -> ~200 taps.

**IIR** (Butterworth, Chebyshev, elliptic): far fewer coefficients, non-linear phase,
can become unstable in fixed point. Fine for audio de-emphasis, DC blockers, notch filters.

Common SDR filters:

| Filter | Use | Notes |
|---|---|---|
| Low-pass FIR (firwin, remez) | Channel selection before decimation | Cutoff = signal BW/2 plus margin |
| Root-raised-cosine (RRC) | Matched filter for PSK/QAM/FSK-with-shaping | alpha 0.2-0.5; use at both TX and RX (RC overall) |
| Gaussian | GFSK/GMSK (Bluetooth BT=0.5, GSM BT=0.3) | Smooth frequency transitions |
| CIC | Very high decimation in FPGA/ASIC | Droop must be compensated with a short FIR |
| Half-band | Decimate by 2 cheaply | Half the taps are zero |
| Polyphase filter bank (PFB) | Channelizer, arbitrary resampler, clock sync | GNU Radio `pfb_*` blocks |
| DC blocker | Remove the DC spike | `y[n] = x[n] - x[n-1] + a*y[n-1]`, a=0.995 |
| Notch | Kill a single carrier/birdie | IIR notch at known offset |
| De-emphasis | WBFM audio (75 us US, 50 us EU/ID) | Single-pole IIR |

Group delay of a symmetric FIR = `(N-1)/2` samples; matters for aligning bursts and timestamps.

## 5. Decimation, interpolation, resampling

- **Decimate by N**: low-pass to `fs/(2N)` first, then keep every Nth sample. Skipping the
  filter aliases everything above the new Nyquist back into the band.
  `scipy.signal.decimate(x, N, ftype="fir", zero_phase=True)` (N <= 13 per stage; chain
  stages for large factors), or `resample_poly(x, up, down)` for rational ratios.
- **Interpolate by M**: insert zeros, then low-pass at the original Nyquist and scale by M.
- **Rational resampler** (`up/down`) converts e.g. 2.4 MS/s -> 48 kS/s (`up=1, down=50`), or
  250 kS/s -> 48 kS/s (`up=24, down=125`).
- **Arbitrary resampler** (`pfb_arb_resampler`, `scipy.signal.resample_poly` with big
  integers, or Farrow) for irrational ratios or when tracking a clock.
- **Frequency translation + decimation** in one step (GNU Radio `freq_xlating_fir_filter`):
  multiply by `e^{-j 2 pi f_off n / fs}`, FIR low-pass, decimate. This is the single most
  used channelization block.
- Stage decimation for efficiency: 2.4 MS/s -> 240 kS/s (by 10) -> 48 kS/s (by 5) needs far
  fewer taps than a single 50x filter with a 24 kHz transition band.

## 6. Mixing and frequency shifting

- Shift a complex signal by `f_off`: `x * exp(-2j*pi*f_off*n/fs)` moves a signal at
  `+f_off` down to 0 Hz. Use a phase accumulator (`np.cumsum` of phase increment, mod 2 pi)
  for long streams to avoid float precision loss in `n`.
- Real mixing (multiplying by cos) produces both sum and difference products; complex
  mixing produces only one, which is the entire reason IQ exists.
- **Images**: an imperfect IQ front-end (gain/phase mismatch between I and Q) leaves a
  mirror image at `-f` attenuated by the image rejection ratio (RTL-SDR ~30-40 dB, HackRF
  ~30 dB, USRP >45 dB with calibration). Software IQ balance (Moseley-Slump algorithm,
  GNU Radio `IQ Balance`) improves it.
- **DC spike** at 0 Hz comes from LO leakage and ADC offset. Cures: tune 100-500 kHz off
  the signal and shift in software (the standard trick), enable `offset_tuning` on E4000
  tuners, or apply a DC blocker after the mixer.

## 7. Gain control (AGC)

- Hardware gain stages: LNA (sets noise figure, first stage), mixer/IF gain, baseband VGA.
  Maximize the first stage until intermod appears, keep later stages moderate.
- Software AGC: track the envelope with fast attack (ms) and slow decay (100 ms-1 s):
  `gain *= (1 + rate*(target - |y|))`. GNU Radio `agc2_cc` (attack/decay) is the standard.
- For bursty digital signals use **per-burst normalization** instead of a continuous AGC, or
  the AGC will pump on the preamble.
- Digital demodulators (PSK) need a constant-amplitude constellation; run AGC before the
  Costas loop. FSK/FM demodulators are amplitude-insensitive (limiter behavior).

## 8. Synchronization: carrier, timing, frame

Any coherent digital demod needs three locks, in this order:

1. **Coarse frequency** (within a fraction of the symbol rate): FFT of `x^M` (M = PSK order)
   gives a line at `M*f_off`; or use a known preamble correlation.
2. **Symbol timing**: choose the sample instant per symbol.
   - Mueller & Muller (decision-directed, needs carrier lock first, cheap).
   - Gardner (works before carrier lock, needs 2 samples/symbol).
   - Polyphase clock sync / `Symbol Sync` block (filterbank of matched filters, best default).
   - For FSK/OOK: zero-crossing or preamble-edge timing after demod is often enough.
3. **Carrier phase**: Costas loop (BPSK 2nd order, QPSK 4th order, 8PSK), PLL on a pilot,
   or decision-directed. Loop bandwidth `2*pi/100 .. 2*pi/400` (rad/sample) is a starting
   point; narrower is more accurate but slower and less tolerant of drift.
   Differential modulation (DBPSK/DQPSK) avoids the carrier-phase loop entirely.
4. **Frame sync**: correlate against the sync word/preamble (`Correlate Access Code` with
   allowed bit errors), then extract length, payload, CRC.

Phase ambiguity: a Costas loop locks at M possible phases; resolve with differential
coding or a known sync word (try all M rotations).

## 9. Noise, SNR, sensitivity, link math

- Thermal noise: `-174 dBm/Hz` at 290 K. Noise power in bandwidth B: `-174 + 10*log10(B)`.
  Add receiver noise figure NF. Example NBFM 12.5 kHz, NF 5 dB: `-174 + 41 + 5 = -128 dBm`
  noise floor; needing 12 dB SINAD gives ~-116 dBm sensitivity.
- **Noise figure cascade (Friis)**: `F = F1 + (F2-1)/G1 + ...` in linear units. A 0.8 dB
  NF, 20 dB gain LNA at the antenna followed by a 6 dB NF RTL-SDR gives total NF ~1.0 dB.
  Putting 3 dB of coax before the LNA adds 3 dB straight to NF.
- **Eb/N0** vs SNR: `Eb/N0 = SNR + 10*log10(B / R_b)`. BER targets at 1e-5: BPSK/QPSK
  ~9.6 dB, non-coherent 2FSK ~13.4 dB, 16QAM ~13.4 dB, 64QAM ~17.8 dB (uncoded AWGN).
  Coding (convolutional, LDPC, turbo) buys 3-9 dB.
- **Intermodulation / IP3**: two strong signals at f1, f2 create products at 2f1-f2 and
  2f2-f1 that fall in-band. Third-order products grow 3 dB per 1 dB of input. Lower gain or
  add a filter; RTL-SDR IIP3 is poor (~-10 dBm), SDRplay/Airspy better.
- **Phase noise** of the LO smears close-in spectrum; it limits reception of weak signals
  next to strong ones and limits high-order QAM. RTL-SDR phase noise is mediocre, USRP/Pluto
  fine for QAM-64.
- **Reciprocal mixing**: LO phase noise multiplies with a strong adjacent carrier and raises
  the local noise floor.

## 10. Symbol-rate and modulation-order estimation (blind)

- **Envelope spectrum**: FFT of `|x|^2` shows a line at the symbol rate `R_s` for any
  linearly modulated signal with pulse shaping (also OOK/ASK bursts). Peak of the line
  above the noise gives `R_s`; harmonics may appear.
- **Cyclostationary**: FFT of `x^2` shows lines at `2*f_off` (BPSK) and at `2*f_off +- R_s`;
  FFT of `x^4` shows `4*f_off` for QPSK. If `x^2` has a line but `x^4` is stronger and `x^2`
  is not, suspect QPSK; if `x^2` has a clean line, suspect BPSK. 8PSK needs `x^8`.
- **FSK**: the PSD shows two (2FSK) or four (4FSK) humps separated by the deviation
  (`2*dev`); the instantaneous frequency histogram shows discrete levels.
- **Autocorrelation** of `|x|` reveals burst repetition period, TDMA slot length, and
  spreading sequences (DSSS) as periodic peaks.
- **OFDM**: cyclic prefix causes an autocorrelation peak at the useful symbol length `T_u`;
  subcarrier spacing = `1/T_u`. Flat-topped, rectangular spectrum.
- **Chirp (LoRa)**: linear frequency ramps on the waterfall; dechirp by multiplying with a
  conjugate reference chirp and FFT to get symbols.

## 11. Numeric practicalities

- Use `complex64` (cf32) internally; `complex128` doubles memory for no benefit at 8-14 bits.
- Keep signals scaled to roughly `|x| <= 1`. Convert integer formats with the correct
  divisor (127.5 for cu8/cs8, 2048 for 12-bit-in-16, 32767 for full 16-bit).
- Process in blocks (e.g. 2^18 samples) with filter state carried across blocks
  (`scipy.signal.lfilter` with `zi`) for streaming; never concatenate whole captures unless
  they fit comfortably in RAM.
- Timestamps: GNU Radio `rx_time` tags and SigMF `core:datetime` are the only reliable time
  references; file mtime is not.
- Group delay and filter warm-up eat the first `N_taps` samples of any burst; pad captures
  with 1-2 ms of pre-roll.

## 12. Quick derivations you will be asked for

- Minimum `fs` for a 200 kHz WBFM channel: >= 250 kS/s; practical RTL-SDR: 1.0-2.4 MS/s
  then decimate by 4-10.
- How many taps for a 12.5 kHz channel filter at 240 kS/s with 60 dB rejection and 5 kHz
  transition: `(60-8)/(2.285*2*pi*5e3/240e3) ~= 174 taps`.
- Time to record 30 s at 2.4 MS/s in cu8: `2.4e6 * 30 * 2 = 144 MB`.
- Bin size to resolve two FT8 tones 6.25 Hz apart at 12 kS/s: need `df <= 3 Hz` ->
  `N_FFT >= 4096` (df = 2.93 Hz).
- FSK deviation of a signal whose two humps are 50 kHz apart: `dev = 25 kHz`; modulation
  index `h = 2*dev / R_s` (for R_s 38.4 kbaud, h = 1.3).
