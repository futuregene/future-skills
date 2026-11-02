# Signal Identification

A procedure and a lookup table for turning "what is that on the waterfall?" into an answer.

## 1. Procedure

1. **Frequency first.** The center frequency plus a band plan usually names the service before
   any DSP. Keep an allocation chart handy (ITU, or your national regulator, or sigidwiki band pages).
   Note the ITU Region (1 = Europe/Africa/Middle East/former USSR, 2 = Americas, 3 = Asia-Pacific
   incl. Indonesia); allocations differ.
2. **Measure the six numbers**: center, occupied bandwidth (-20 dB and -3 dB), on/off pattern
   (continuous / bursty / periodic), burst length and period, number of parallel channels,
   symmetry. `python scripts/iq_info.py cap --fs .. --fc ..` prints most of these.
3. **Classify the shape** with the table below.
4. **Estimate symbol rate / deviation / modulation order**: `python scripts/symbol_rate.py cap --fs ..`
   or inspectrum cursors, or the `x^2`/`x^4` trick.
5. **Cross-reference** on sigidwiki.com by frequency and bandwidth; the site has audio/waterfall
   samples for hundreds of signals.
6. **Confirm by decoding**: run the candidate decoder; a valid CRC/checksum or readable output
   is proof.

## 2. Band cheat sheet (where common things live)

| Range | Typical occupants |
|---|---|
| < 30 kHz (VLF) | Submarine comms, time signals, natural radio |
| 30-300 kHz (LF) | Time signals (DCF77 77.5k, WWVB 60k, MSF 60k, JJY), NDBs, longwave broadcast (EU) |
| 300 kHz-3 MHz (MF) | AM broadcast (MW 531-1602), NAVTEX 518k, marine, 160 m ham (1.8-2.0) |
| 3-30 MHz (HF) | Shortwave broadcast, ham bands (80/40/30/20/17/15/12/10 m), aeronautical/marine SSB, HFDL, WSPR/FT8, RTTY, STANAG, CODAR/radar, over-the-horizon radar |
| 30-50 MHz | Low-band VHF land mobile, remote controls, 6 m ham (50-54), sporadic-E |
| 50-88 MHz | 6 m ham, VHF band I TV (legacy), business |
| 87.5-108 MHz | FM broadcast + RDS |
| 108-137 MHz | Airband: VOR/ILS (108-118 AM nav), voice (118-137 AM 8.33/25 kHz), ACARS 131.x, VDL2 136.x |
| 137-138 MHz | Weather satellites (APT/LRPT), Orbcomm, some space |
| 144-148 MHz | 2 m ham (APRS 144.39/144.8, FM, SSB, satellites) |
| 148-174 MHz | VHF land mobile, marine VHF (156-162, AIS 161.975/162.025), pagers, weather radio (162.4-162.55) |
| 225-400 MHz | Military air/SATCOM (UHF milsat ~240-270, 340-400), some ham 219-225 |
| 400-406 MHz | Radiosondes, satellite uplinks, Argos |
| 420-450 MHz | 70 cm ham, ISM 433.05-434.79 (Region 1), radar |
| 450-470 MHz | UHF land mobile, DMR/P25/NXDN, GMRS/FRS (462-467, US) |
| 470-698 MHz | UHF TV (DVB-T/ATSC), wireless mics |
| 758-894 MHz | LTE/5G, public safety 700/800, cellular |
| 863-870 / 902-928 MHz | ISM/SRD (LoRa, rtl_433 868/915, RFID), 33 cm ham (US) |
| 920-925 MHz | LoRa/IoT (Indonesia 920-923), RFID |
| 925-960 / 1710-1785 / 1805-1880 | GSM/LTE 900/1800 |
| 1090 / 978 MHz | ADS-B / UAT |
| 1176-1610 MHz | GNSS (L5 1176, L2 1227, L1 1575, GLONASS 1602), Inmarsat/Iridium (1518-1626) |
| 2.4-2.4835 GHz | Wi-Fi, Bluetooth, Zigbee, ISM, microwave ovens, video senders |
| 3.3-3.8 / n78 | 5G mid-band, WiMAX legacy, amateur 9 cm |
| 5.15-5.85 GHz | Wi-Fi 5/6, ISM, amateur 5 cm, weather radar |
| 5.8 GHz | FPV drone video, ISM |
| 10-10.5, 24, 76-81 GHz | Amateur/radar, ISM 24 GHz, automotive radar 77 GHz |

## 3. Shape-to-mode table

| What you see | Candidate | Discriminator |
|---|---|---|
| Single carrier line, no modulation | Beacon, CW idle, pilot, birdie/spur | Does it move with `fc`? then it is a device spur, not real |
| Carrier + two symmetric sidebands | AM (broadcast, airband) | Envelope gives audio |
| One-sided ~2.7 kHz lump, no carrier | SSB voice | Sounds natural only when tuned within 50 Hz |
| Narrow (60 Hz) two-tone warble | PSK31 / RTTY / FT8 in an audio slice | Decode in fldigi/WSJT-X |
| 10-16 kHz flat-ish hump, bursty voice | NBFM voice | Discriminator gives clean audio; 12.5/25 kHz spacing |
| ~180 kHz dense, 19 kHz pilot visible | WBFM broadcast | RDS line at 57 kHz |
| Two distinct humps | 2FSK | Spacing = 2 x deviation |
| Four evenly spaced humps / 4-level inst. freq | 4FSK (DMR/P25/NXDN) | 4800 baud line; DMR has 30 ms TDMA bursts on two slots |
| Rounded single lump, constant envelope | GMSK/MSK/GFSK | `x^2` line at 2 f_off +- R_s/2 |
| Rounded lump, on/off in slots | GSM (GMSK, 200 kHz, 577 us bursts) | 8-slot TDMA frame 4.615 ms |
| RRC/sinc lump, varying envelope | PSK/QAM | `x^2` (BPSK) or `x^4` (QPSK) spectral line |
| Flat-topped rectangle, sharp edges | OFDM (Wi-Fi/LTE/DAB/DVB) | Autocorrelation peak at symbol length; pilots |
| Diagonal frequency ramps | LoRa / CSS | Preamble up-chirps + 2.25 down-chirps |
| Short bursts hopping across a wide band | FHSS (Bluetooth, telemetry) | 1 MHz grid + 625 us slots = Bluetooth |
| On/off keyed bursts, few kHz wide, at 315/433/868/915 | OOK/ASK remote or sensor | rtl_433 -A; measure pulse widths |
| Wide, buried in noise, sinc envelope | DSSS (GPS, CDMA) | Correlate with known PN code |
| Trapezoid/chirp sweeping repeatedly | Radar / CODAR / OTH / ramp jammer | Period and sweep width; CODAR ~25 MHz coastal |
| Vertical "rain" across the whole span | Impulsive noise (switching PSU, PLC, ignition) | Disappears when you unplug the offender |
| Comb of evenly spaced lines | Harmonics of a clock/spur, or a birdie comb | Spacing = fundamental; moves with device, not antenna |
| Symmetric mirror of a real signal about `fc` | IQ image / DC-side artifact | Reduce gain / enable IQ correction; it is not a real signal |

## 4. Telling artifacts from real signals

- **DC spike at exactly `fc`**: LO leakage; always there; ignore or tune off-center.
- **Birdies/spurs**: fixed offsets from `fc` that move when you retune the SDR (they track the
  ADC/clock, not the antenna). Change `fs` and watch which lines move.
- **Images**: a mirror of a strong signal at `-f` relative to it; weaker; fixed by IQ balance.
- **Aliases**: strong out-of-band signal folding in when `fs` is too low or filtering is weak;
  appears/moves oddly when you change `fs`.
- **Front-end overload / intermod**: many evenly related "signals" that all vanish when you drop
  gain 10 dB; classic near strong FM/pager/cell sites.
- **Test**: disconnect the antenna. Anything that remains is internal (spur/image/DC), not off-air.

## 5. Bandwidth-to-symbol-rate quick math

- FSK: `occupied BW ~= 2*dev + R_s` (Carson-ish). Two humps 50 kHz apart -> dev 25 kHz.
- PSK/QAM with RRC roll-off alpha: `BW ~= R_s*(1+alpha)`; alpha usually 0.2-0.5. A 40 kHz lump
  at alpha 0.35 -> `R_s ~= 40e3/1.35 ~= 29.6 kbaud`.
- OFDM: `subcarrier spacing = fs_used / N_FFT`; total BW ~= used subcarriers x spacing.
- OOK: `BW ~= 2 * bit_rate` for NRZ; measure pulse widths directly instead.

## 6. Recording for identification

- Use the smallest `fs` that still contains the whole signal plus 20 % margin (better dynamic range,
  smaller files). But if you might have missed adjacent channels, do one wide survey capture first.
- 10-30 s captures catch periodic bursts. For very slow beacons (FT8 15 s, WSPR 2 min) record a
  full cycle.
- Save `fc`, `fs`, gain, antenna, time, location (SigMF). Note anything you did to the front end
  (LNA, filter, attenuator) since it changes levels.
