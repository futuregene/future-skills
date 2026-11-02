# Modulation and Demodulation Reference

For each mode: how it looks, key parameters, demodulation algorithm, GNU Radio blocks,
numpy one-liner where practical, and where it is used.

## 1. Analog modes

### AM (DSB with carrier)

- **Look**: carrier line with two symmetric sidebands; bandwidth = 2 x audio BW
  (broadcast MW 9/10 kHz channels, airband 8.33/25 kHz channels).
- **Demod (envelope)**: `audio = |x|`, then DC block and low-pass at 3-5 kHz.
  Coherent (synchronous) AM: PLL to the carrier, take real part; better for fading/selective
  fading, used by SDR++ "AM sync".
- **GNU Radio**: `Complex to Mag` -> `DC Blocker` -> `Low Pass` -> audio; or `AM Demod` hier block.
- **Used by**: MW/SW broadcast, VHF airband (118-137 MHz), CB (27 MHz), some marine HF.

### DSB-SC / SSB (USB, LSB)

- **Look**: no carrier; one sideband only (USB above, LSB below a suppressed carrier). Voice
  SSB is 2.4-3 kHz wide; it sounds like Donald Duck until tuned within ~50 Hz.
- **Demod**: shift so the suppressed carrier is at 0 Hz, then filter one side:
  USB = low-pass of the complex signal after shifting by `-f_carrier`, take real part;
  equivalently Weaver or Hilbert (phasing) method. `audio = np.real(x_shifted_filtered)`.
- **GNU Radio**: `Frequency Xlating FIR Filter` (complex band-pass taps 300-3000 Hz for USB,
  -3000 to -300 for LSB) -> `Complex to Real` -> AGC -> audio.
- **Used by**: amateur HF voice (LSB below 10 MHz by convention, USB above), marine/aero HF,
  military HF, digital modes ride on USB (FT8, PSK31, RTTY via AFSK).

### CW (Morse)

- Keyed carrier. Demod by shifting to ~600-800 Hz beat note and taking the real part; decode
  with envelope + timing (dit/dah) or tools like fldigi/CW Skimmer.

### NBFM (narrowband FM)

- **Look**: 10-16 kHz wide, steady carrier-like hump; 12.5 or 25 kHz channel spacing.
  Deviation 2.5 kHz (12.5 kHz channels) or 5 kHz (25 kHz).
- **Demod**: FM discriminator `np.angle(x[1:] * np.conj(x[:-1]))` (gives instantaneous
  frequency in rad/sample; scale by `fs/(2*pi*dev)` for unit audio). Then de-emphasis
  (optional for NBFM), low-pass 3 kHz, squelch on signal power or noise level.
- **GNU Radio**: `NBFM Receive` (quad_rate = 4*audio_rate is typical) or `Quadrature Demod`
  with gain `fs/(2*pi*dev)`.
- **Used by**: amateur VHF/UHF, PMR446/FRS/GMRS, marine VHF (156-162 MHz), business radio,
  analog trunking, APRS (AFSK1200 over NBFM), POCSAG (direct FSK at baseband).

### WBFM (broadcast FM, 88-108 MHz)

- **Look**: ~180-250 kHz wide, dense. 75 kHz deviation, 19 kHz pilot, stereo subcarrier at
  38 kHz (DSB-SC L-R), RDS at 57 kHz (BPSK 1187.5 bps).
- **Demod**: discriminator at 200-250 kS/s -> mono = low-pass 15 kHz; stereo = PLL on 19 kHz
  pilot, double it to 38 kHz, demod L-R, matrix; RDS = band-pass 57 kHz +-2.4 kHz, BPSK demod
  with `Symbol Sync` at 1187.5 baud (gr-rds).
  De-emphasis 75 us (Americas, Korea, Japan) or 50 us (Europe, Indonesia, most of the world).
- **GNU Radio**: `WBFM Receive` (quad_rate, audio_decimation) or `WBFM Receive PLL` for stereo.

### Other analog

- **SSTV**: FM-modulated audio tones (1200/1500-2300 Hz) on SSB/FM; decode with QSSTV, MMSSTV.
- **NOAA APT**: 2400 Hz AM subcarrier inside a 34 kHz-deviation WBFM signal; demod FM, then AM
  envelope, then sample lines at 4160 pixels/s (SatDump, noaa-apt).
- **Analog TV (PAL/NTSC)**: vestigial sideband AM video + FM audio; rare now, SDRangel has an ATV demod.

## 2. Digital modes: amplitude and frequency

### OOK / ASK

- **Look**: carrier bursts turning on/off; bandwidth ~2 x bit rate; often at 315/433.92/868/915 MHz.
  Encodings: PWM (short/long pulses), Manchester, PPM, raw NRZ. Preamble of alternating bits.
- **Demod**: `env = |x|` low-passed -> threshold (adaptive: mean of max/min in window) ->
  measure pulse widths -> decode encoding. rtl_433 does this generically (`-A` analyze mode).
- **GNU Radio**: `Complex to Mag` -> `Low Pass` -> `Threshold` -> `Symbol Sync` (or edge timing).
- **Used by**: key fobs (fixed or rolling code), weather sensors, doorbells, TPMS (some), RFID 125 kHz-ish.

### 2FSK / 4FSK / GFSK / MSK / GMSK

- **Look**: two (or four) humps separated by `2*dev` (2FSK) or evenly spaced (4FSK); GFSK
  humps are smoother, MSK/GMSK looks like one rounded lump.
  Modulation index `h = 2*dev/R_s`; MSK is h=0.5, GSM GMSK h=0.5 BT=0.3, Bluetooth h~0.32-0.35 BT=0.5.
- **Demod (non-coherent)**: discriminator -> low-pass at ~R_s -> `Symbol Sync` -> slicer
  (2 levels or 4 levels). Alternatively two/four band-pass filters and compare energies
  (better for low SNR, insensitive to frequency offset if filters are wide).
  Coherent MSK/GMSK: treat as OQPSK with sinusoidal shaping (Laurent decomposition), needs
  Costas; gr-gsm does this for GSM.
- **GNU Radio**: `Quadrature Demod` -> `Low Pass` -> `Symbol Sync (TED: Gardner or M&M)` ->
  `Binary Slicer`; or `GFSK Demod` hier block; 4FSK: quantize into 4 levels (`Quantizer` / custom).
- **Used by**: POCSAG/FLEX pagers (2FSK 512/1200/2400 bps, dev 4.5 kHz), DMR/P25 Phase 1/NXDN
  (4FSK / C4FM 4800 baud, deviations +-1944/648 Hz for DMR, +-1800/600 for P25),
  Bluetooth BR (GFSK 1 Mbps, dev 157 kHz), BLE (GFSK 1 Mbps, dev 250 kHz), GSM (GMSK 270.833 kbaud),
  ISM sensors (FSK 38.4 kbps typical, CC1101/Si4432 family), radiosondes (RS41 GFSK 4800 bd),
  AIS (GMSK 9600 bd), APRS AFSK 1200 (tones 1200/2200 Hz inside NBFM), RTTY (AFSK 45.45 bd, 170 Hz shift).

## 3. Digital modes: phase and quadrature

### BPSK / QPSK / OQPSK / 8PSK / DPSK

- **Look**: sinc-shaped (with RRC: rounded-shoulder) lump of width `R_s*(1+alpha)`; no
  carrier line. `x^2` FFT line at `2*f_off` for BPSK; `x^4` for QPSK. OQPSK avoids zero
  crossings (constant envelope-ish, used by 802.15.4/Zigbee 2.4 GHz at 2 Mchip/s and many satellites).
- **Demod (coherent)**: AGC -> coarse freq correction -> RRC matched filter (alpha 0.35 typical)
  -> `Symbol Sync` (2 sps) -> `Costas Loop` (order 2/4/8) -> `Constellation Decoder` ->
  `Differential Decoder` (if DPSK/differential coding) -> unpack bits -> frame sync.
- **Demod (differential, cheap)**: `np.angle(x[1:]*np.conj(x[:-1]))` on symbol-spaced samples,
  quantize phase differences; tolerates frequency offset up to a fraction of R_s.
- **Used by**: satellites (NOAA HRPT QPSK 665 kbps, Meteor LRPT QPSK/OQPSK 72k/80k symbols,
  GOES HRIT BPSK 927 kbps, most cubesats BPSK 1.2-9.6 kbps), RDS (BPSK 1187.5),
  PSK31 (BPSK 31.25 bd on HF audio), GPS L1 C/A (BPSK 1.023 Mchip/s spread), DVB-S QPSK,
  telemetry links, Wi-Fi/LTE pilots.

### QAM (16/64/256/1024)

- **Look**: like PSK spectrally; constellation is a square grid. Needs high SNR (16QAM ~20 dB
  for clean, 256QAM ~30+ dB) and good phase noise.
- **Demod**: as PSK plus amplitude-aware AGC, decision-directed equalizer (CMA -> LMS), and
  usually a pilot/training sequence. Rarely blind-demodulated in hobby SDR.
- **Used by**: DVB-C (64/256QAM 6.9 Mbaud), cable modems, microwave backhaul, single-carrier
  in DOCSIS/ATSC 3.0 subcarriers, inside OFDM subcarriers (Wi-Fi, LTE, DAB uses DQPSK).

### OFDM

- **Look**: flat-topped rectangular spectrum with sharp edges (Wi-Fi 20 MHz, LTE 1.4/3/5/10/15/20 MHz,
  DAB 1.536 MHz, DVB-T 6/7/8 MHz, DRM 10 kHz on HF). Pilots may show as lines.
- **Parameters**: FFT size N, subcarrier spacing `fs_ofdm/N` (LTE 15 kHz, Wi-Fi 312.5 kHz,
  DAB 1 kHz), cyclic prefix length, pilot layout.
- **Demod**: CP-based timing/frequency sync (autocorrelation at lag N), FFT, channel estimate
  from pilots, equalize per subcarrier, demap. Practical decoders: `gr-dab`, `welle.io` (DAB),
  `leandvb`/`gr-dvbt` (DVB), `srsRAN`/`LTE-Cell-Scanner` (LTE), `gr-ieee802-11` (Wi-Fi 802.11a/g/p).
- **Used by**: Wi-Fi, LTE/5G NR, DAB+, DVB-T/T2, DRM, ATSC 3.0, PLC, some IoT.

## 4. Spread spectrum

### DSSS / CDMA

- Data XOR chip sequence at chip rate `R_c >> R_b`; spectrum looks like a wide sinc lump
  below the noise floor (GPS L1 C/A is ~20 dB below noise at the antenna).
- **Demod**: correlate with the known PN code (acquisition: search code phase x Doppler grid;
  tracking: DLL for code, PLL/FLL for carrier). GNSS-SDR does this fully; gr-ieee802-15-4 for
  Zigbee DSSS-OQPSK (32-chip sequences per 4-bit symbol).
- **Used by**: GPS/GNSS, Zigbee/802.15.4, CDMA2000/UMTS (obsolete-ish), some telemetry.

### FHSS

- Narrow bursts hopping across channels (Bluetooth 79 x 1 MHz, 1600 hops/s; some ISM
  telemetry, military). Capture the whole hop band (needs wide `fs`, e.g. 20+ MHz for Bluetooth),
  then demodulate hop by hop with channel detection. Hobby-level: Ubertooth for BT; SDR with
  wide bandwidth (BladeRF/USRP) for research.

### CSS / LoRa

- **Look**: linear up-chirps (preamble ~8-12 chirps) followed by 2.25 down-chirps (sync +
  SFD), then data chirps shifted in start frequency. BW 125/250/500 kHz (also 7.8-62.5 kHz),
  spreading factor SF7-12 (chirp length `2^SF / BW`).
- **Demod**: multiply by conjugate base chirp (dechirp) -> FFT of length `2^SF` -> peak bin =
  symbol; then gray demap, deinterleave, Hamming decode, dewhiten, CRC.
  `gr-lora_sdr` (Tapparel) implements a full LoRa PHY TX/RX; `LoRa-SDR`, `rpp0/gr-lora` for RX.
- **Used by**: LoRaWAN (EU 868, US 915, ID 920-923 MHz), Meshtastic, LoRa APRS (433.775 MHz EU).

## 5. Identification cheat table

| Waterfall shape | Likely mode | Confirm by |
|---|---|---|
| Carrier line with symmetric sidebands | AM | Envelope gives audio |
| One-sided 3 kHz lump, no carrier | SSB | Tune until voice is natural |
| 10-16 kHz steady hump | NBFM | Discriminator gives clean audio |
| 200 kHz wide with 19 kHz pilot | WBFM broadcast | RDS at 57 kHz |
| Two humps, constant spacing | 2FSK | Instantaneous frequency has 2 levels |
| Four evenly spaced humps or 4-level inst freq | 4FSK (DMR/P25/NXDN) | 4800 baud symbol-rate line; TDMA slots for DMR (30 ms) |
| Single rounded lump, no humps, constant envelope | GMSK/MSK | `x^2` line at 2 f_off +- R_s/2 |
| Sinc/RRC lump, varying envelope | PSK/QAM | `x^2` or `x^4` spectral line |
| Rectangular flat top, sharp edges | OFDM | Autocorrelation peak at N samples |
| Diagonal ramps | LoRa/CSS | Dechirp gives lines |
| Short bursts hopping around | FHSS (Bluetooth) | 1 MHz channel grid, 625 us slots |
| Wide, below noise, sinc envelope | DSSS (GPS) | Correlate with PN code |
| On/off bursts, few kHz wide, at 433/315 | OOK | Envelope shows pulses; rtl_433 -A |

## 6. Standard parameter values (memorize)

| System | Modulation | Symbol/bit rate | Deviation / BW |
|---|---|---|---|
| POCSAG | 2FSK | 512/1200/2400 bps | +-4.5 kHz |
| FLEX | 2/4FSK | 1600/3200/6400 bps | +-4.8 kHz |
| DMR | 4FSK | 4800 baud (9600 bps) | +-1944 / +-648 Hz, 12.5 kHz |
| P25 Phase 1 | C4FM (4FSK) | 4800 baud | +-1800 / +-600 Hz |
| NXDN 4800 | 4FSK | 2400 baud | 6.25 kHz |
| TETRA | pi/4-DQPSK | 18 kbaud (36 kbps) | 25 kHz |
| dPMR | 4FSK | 2400 baud | 6.25 kHz |
| D-STAR | GMSK | 4800 bps | 6.25 kHz |
| AIS | GMSK | 9600 bps | 25 kHz channels at 161.975/162.025 |
| APRS | AFSK 1200 (Bell 202) in NBFM | 1200 bps | tones 1200/2200 Hz |
| ADS-B 1090ES | PPM | 1 Mbps | ~2 MHz |
| UAT 978 | CPFSK | 1.04167 Mbps | 1.3 MHz |
| ACARS VHF | AM-MSK (2400 bd) | 2400 bps | 131.550 MHz (US), 131.725 (EU) |
| VDL Mode 2 | D8PSK | 10.5 kbaud (31.5 kbps) | 136.975 MHz |
| GSM | GMSK BT=0.3 | 270.833 kbaud | 200 kHz |
| Bluetooth BR | GFSK BT=0.5 | 1 Mbps | +-157.5 kHz, 1 MHz ch |
| BLE | GFSK | 1 Mbps (2 M, 125/500 k coded) | +-250 kHz, 2 MHz ch |
| Zigbee 2.4 | OQPSK DSSS | 250 kbps, 2 Mchip/s | 2 MHz, 5 MHz spacing |
| LoRa | CSS | SF7-12 | 125/250/500 kHz |
| Wi-Fi 802.11g | OFDM 52 sc | 6-54 Mbps | 20 MHz |
| LTE | OFDMA | 15 kHz sc | 1.4-20 MHz |
| NOAA APT | AM-on-WBFM | 4160 px/s | 34 kHz dev, ~40 kHz |
| Meteor-M LRPT | QPSK/OQPSK | 72 or 80 ksym/s | 137.1/137.9 MHz |
| GOES HRIT | BPSK | 927 kbps | 1694.1 MHz |
| RS41 radiosonde | GFSK | 4800 bd | 400-406 MHz |
| RDS | BPSK | 1187.5 bps | 57 kHz subcarrier |
| FT8 | 8-GFSK | 6.25 baud | 50 Hz, 15 s slots |
| WSPR | 4FSK | 1.4648 baud | 6 Hz, 2 min |
| PSK31 | BPSK | 31.25 baud | ~60 Hz |
| RTTY (amateur) | AFSK/FSK | 45.45 baud | 170 Hz shift |

## 7. Writing a demodulator from scratch: order of operations

1. Capture with margin (fs >= 4 x BW) and verify the signal visually.
2. Shift to 0 Hz, low-pass to ~1.2 x BW, decimate to 4-8 samples per symbol.
3. Normalize amplitude (AGC or per-burst).
4. Apply the mode-specific detector (envelope / discriminator / matched filter).
5. Recover timing (Gardner/M&M/polyphase; or edge-based for OOK/FSK).
6. Slice to symbols; for coherent PSK recover carrier first (Costas), resolve phase ambiguity.
7. Find the preamble / sync word; align frames; apply descrambler, deinterleaver, FEC, CRC.
8. Validate on a known-good capture (record your own device transmitting known data).
9. Only then optimize (loop bandwidths, filter lengths, fixed point).
