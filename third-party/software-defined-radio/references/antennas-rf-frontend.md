# Antennas and RF Front-End

The antenna and the first LNA set what you can hear; no amount of DSP recovers a signal the
front end never captured.

## 1. Antenna basics

- **Wavelength** `lambda = 300 / f_MHz` metres. Antenna sizes scale with lambda.
- **Half-wave dipole**: total length `~= 143 / f_MHz` m (each leg `71.5/f_MHz`), ~2.15 dBi,
  50-73 ohm, bidirectional broadside. The default "known-good" antenna.
- **Quarter-wave monopole/whip**: `71.5 / f_MHz` m over a ground plane (radials or car body),
  omnidirectional, needs a counterpoise.
- **Resonance and SWR**: an antenna cut for `f` is narrowband; off resonance the match degrades
  (SWR rises). For RX-only, SWR matters far less than for TX (you just lose a little signal); for
  TX a high SWR can damage the PA. Aim SWR < 2:1 for TX.
- **Polarization**: match it. Vertical for most terrestrial FM/mobile/APRS; horizontal for SSB/CW
  weak-signal and TV; circular (RHCP/LHCP) for satellites (QFH, turnstile, crossed Yagi). A
  polarization mismatch costs ~3 dB (linear cross) to 20+ dB (linear vs the wrong circular sense).
- **Gain and pattern**: gain comes from focusing energy in a direction. dBi vs dBd: `dBi = dBd + 2.15`.
  A high-gain antenna is directional; you must aim it (or accept it only hears one direction).
- **Take-off angle / height**: for terrestrial VHF/UHF, higher is almost always better (line of
  sight). For HF skywave, angle and ground matter more than height.

## 2. Practical antennas by band and purpose

| Band / use | Antenna | Notes |
|---|---|---|
| Broadband scanning VHF/UHF | Discone, or the RTL-SDR telescopic dipole kit | Discone 25 MHz-1.3 GHz, low gain, omni |
| HF RX (broadband) | Random wire + 9:1 unun + ground, or active mini-whip (PA0RDT), or mag-loop | Active whip is small and quiet if sited away from noise |
| HF TX resonant | Dipole, EFHW (49:1), vertical + radials | Cut per band; use an ATU for multiband |
| FM broadcast / airband | Dipole or discone; airband: 1/4-wave or J-pole tuned to 125 MHz | |
| Marine/AIS 162 MHz | 1/2-wave vertical, marine whip | |
| 137 MHz weather sats | V-dipole (120 deg, legs 53.4 cm, ~0.5 m off ground) or QFH | QFH is circular, best for full passes |
| L-band (1.5-1.7 GHz) Inmarsat/Iridium/GOES | Patch antenna, helix, or small dish/grid + LNA | GOES needs a dish (0.6-1 m) or big grid |
| GNSS 1.575 GHz | Active patch antenna (with bias tee) | |
| ADS-B 1090 MHz | 1/4-wave (6.8 cm) ground plane, colinear, or "spider" | Add 1090 SAW LNA at the antenna |
| 2.4/5 GHz | Patch, panel, Yagi, dish, or biquad | For direction and gain |
| Satellite UHF/VHF (2 m/70 cm) | Crossed Yagi (Arrow/Elk), turnstile, eggbeater | Yagi needs az/el tracking |
| Direction finding | Yagi/loop (manual), or KrakenSDR array (UCA/ULA) | |
| Amateur multi-band vertical | 1/4-wave with a tuner or a commercial vertical | |

DIY dipole length: `each_leg_cm = 7150 / f_MHz`. Example: 137.5 MHz -> 52 cm per leg, ~104 cm tip
to tip; V-dipole for NOAA uses 53.4 cm legs at 120 degrees.

## 3. Coax and connectors

| Cable | Impedance | Loss/100 m @ 1 GHz | Use |
|---|---|---|---|
| RG-174 | 50 | ~120 dB | Very short jumpers only |
| RG-58 | 50 | ~50 dB | Short VHF runs |
| RG-6 (quad-shield) | 75 | ~20 dB | Cheap, low loss; fine for RX; slight mismatch to 50 ohm |
| RG-213 | 50 | ~13 dB | HF/VHF runs |
| LMR-240 | 50 | ~20 dB | Medium runs, flexible |
| LMR-400 | 50 | ~13 dB | Long UHF runs |
| Hardline / LDF | 50 | ~5 dB | Base stations |

- **Loss matters most before the LNA**: 3 dB of coax before the first amplifier adds 3 dB to
  the system noise figure directly. Put the LNA at the antenna, then coax loss only costs signal,
  not noise figure (Friis).
- **75 vs 50 ohm**: RG-6 (75) into a 50-ohm SDR causes a small mismatch (~0.18 dB, SWR 1.5); fine
  for RX. Don't mix for TX.
- **Connectors**: SMA (most SDRs, up to 18 GHz), N (weatherproof, low loss, to 11 GHz), BNC (bench,
  VHF), UHF/PL-259 (HF, not constant-impedance), F (TV/RG-6), MCX/MMCX (dongles), TS9/SMA on some.
  Use the fewest adapters; each adapter adds loss and reflection. Weatherproof outdoor joints
  (self-amalgamating tape).

## 4. LNAs, filters, and gain staging

- **LNA placement**: at the antenna, powered by bias tee. Choose one with low NF (< 1 dB) and
  enough gain (15-20 dB) to overcome coax loss, but not so much that it overloads the SDR or
  itself in the presence of strong signals (check its P1dB/IP3).
- **Filter before LNA** when a strong out-of-band signal (FM broadcast, pager, cell) is present;
  otherwise the LNA generates intermod. A SAW filter + LNA combo (Nooelec SAWbird for 137/1090/1420/
  1575/1690) is the clean solution for one target band.
- **Cascade order**: filter -> LNA -> (coax) -> SDR is ideal outdoors. Indoors with short coax,
  filter -> LNA -> SDR at the desk is fine.
- **Total system NF (Friis)**: `F = F1 + (F2-1)/G1 + (F3-1)/(G1 G2) + ...` (linear). Worked:
  SAW+LNA NF 1.0 dB gain 20 dB, then 3 dB coax (F=2, G=0.5), then RTL-SDR NF 6 dB:
  `F = 1.26 + (2-1)/100 + (4-1)/(100*0.5) = 1.26 + 0.01 + 0.06 = 1.33` linear -> **1.24 dB**.
  Without the LNA: coax 3 dB then SDR 6 dB gives ~9 dB NF. The LNA is worth ~7.7 dB of sensitivity.
- **Don't over-amplify**: two LNAs in series usually overload. One good LNA at the antenna is the rule.

## 5. Link budget

`P_rx (dBm) = P_tx + G_tx - L_path - L_cable_tx - L_cable_rx + G_rx`

- **FSPL** `L = 20 log10(d_km) + 20 log10(f_MHz) + 32.44` dB (free space, line of sight).
- Compare `P_rx` to sensitivity `= -174 + 10 log10(BW_Hz) + NF + required_SNR`.
- Example ADS-B: aircraft EIRP ~51 dBm (125 W + antenna), 200 km, 1090 MHz:
  FSPL `= 20 log10(200) + 20 log10(1090) + 32.44 = 46 + 60.7 + 32.44 = 139.2` dB.
  `P_rx = 51 - 139.2 + 3 (rx antenna) = -85.2 dBm`. Noise in 2 MHz, NF 3 dB with LNA:
  `-174 + 63 + 3 = -108 dBm`; SNR ~23 dB -> easy decode. That is why ADS-B reaches 200-400 km.
- Example LoRa SF12: sensitivity ~-137 dBm; 14 dBm TX, 2 dBi antennas, 915 MHz, budget allows
  ~150 dB path -> multi-km even in clutter.

`scripts/sdr_calc.py` computes FSPL, link budget, noise floor, and dipole lengths.

## 6. Noise and siting

- The biggest RX problem in cities is **local noise** (switching supplies, LED drivers, PLC,
  Ethernet, solar inverters, plasma TVs), not sensitivity. Symptoms: raised noise floor,
  vertical "rain" on the waterfall, S9 hash on HF.
- Cures: move the antenna away from the house/noise, use coax with good shield and a common-mode
  choke (ferrite/1:1 balun at the feedpoint), ferrite the USB and power cables, run the SDR on a
  laptop on battery to test, add band-pass filtering, try a remote/loop antenna.
- **Ground and safety**: ground the mast; use a lightning arrestor/gas discharge tube on the coax;
  disconnect antennas in storms. Keep antennas clear of power lines (fatal contact risk).
- **RF exposure** (TX): keep people out of the near field of transmitting antennas; follow the
  regulator's MPE limits, especially for higher-power HF/VHF.

## 7. Measuring your antenna

- **NanoVNA** (cheap vector network analyzer, 50 kHz-1.5/3 GHz): measure SWR/return loss vs
  frequency to confirm resonance and match; measure cable loss and length (TDR). Essential and inexpensive.
- **RTL-SDR + noise source + `rtl_power`**: rough frequency response.
- **Known reference signal**: compare received level of a stable broadcast/beacon before and after
  changes to judge antenna/LNA improvements.
- For RX-only, a "good enough" antenna that is resonant-ish and sited away from noise beats a
  fancy antenna next to a switching supply.
