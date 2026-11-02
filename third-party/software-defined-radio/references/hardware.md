# SDR Hardware Reference

Specs are manufacturer figures as of 2026; sustained rates over USB are lower than the
ADC maximum on many devices. "Driver" names are what SoapySDR / GNU Radio use.

## 1. Comparison table

| Device | Freq range | Max BW / rate | Bits | TX | Duplex | Clock | USB | Driver | Price tier |
|---|---|---|---|---|---|---|---|---|---|
| RTL-SDR Blog V3 | 500 kHz-1.766 GHz (HF via direct sampling) | 2.4 MS/s (3.2 max) | 8 | no | - | 1 ppm TCXO | 2.0 | rtlsdr | $ |
| RTL-SDR Blog V4 | 500 kHz-1.766 GHz (HF via built-in upconverter) | 2.4 MS/s | 8 | no | - | 1 ppm TCXO | 2.0 | rtlsdr (blog fork) | $ |
| Generic RTL2832U dongle | 24 MHz-1.7 GHz | 2.4 MS/s | 8 | no | - | 20-60 ppm | 2.0 | rtlsdr | $ |
| Nooelec NESDR SMArt/SMArTee | 25 MHz-1.75 GHz | 2.4 MS/s | 8 | no | - | 0.5 ppm | 2.0 | rtlsdr | $ |
| Airspy Mini | 24 MHz-1.8 GHz | 6 MS/s (3 M alt) | 12 | no | - | 0.5 ppm | 2.0 | airspy | $$ |
| Airspy R2 | 24 MHz-1.8 GHz | 10 MS/s (2.5 M alt) | 12 | no | - | 0.5 ppm, ext clock in | 2.0 | airspy | $$ |
| Airspy HF+ Discovery | 0.5 kHz-31 MHz, 60-260 MHz | 912 kS/s | 18 (eff.) | no | - | 0.5 ppm | 2.0 | airspyhf | $$ |
| SDRplay RSP1B | 1 kHz-2 GHz | 10 MHz | 14 | no | - | 0.5 ppm | 2.0 | sdrplay (closed API) | $$ |
| SDRplay RSPdx / RSPdx-R2 | 1 kHz-2 GHz | 10 MHz | 14 | no | - | 0.5 ppm, ext clk | 2.0 | sdrplay | $$ |
| SDRplay RSPduo | 1 kHz-2 GHz, 2 tuners (coherent) | 10 MHz (2 MHz dual) | 14 | no | - | 0.5 ppm | 2.0 | sdrplay | $$ |
| HackRF One | 1 MHz-6 GHz | 20 MS/s | 8 | yes | half | 20 ppm (TCXO addon), clk in/out | 2.0 | hackrf | $$ |
| ADALM-Pluto | 325 MHz-3.8 GHz (70 M-6 G hacked) | 61.44 MS/s (USB2 ~4-5 M sustained) | 12 | yes | full, 2x2 (hack) | 25 ppm (TCXO 0.5 mod) | 2.0 | plutosdr / iio | $$ |
| LimeSDR Mini 2.0 | 10 MHz-3.5 GHz | 30.72 MS/s (40 MHz BW) | 12 | yes | full 1x1 | 1 ppm, ext ref | 3.0 | lime | $$$ |
| LimeSDR USB | 100 kHz-3.8 GHz | 61.44 MS/s | 12 | yes | full 2x2 | 1 ppm | 3.0 | lime | $$$ |
| BladeRF 2.0 micro xA4/xA9 | 47 MHz-6 GHz | 61.44 MS/s | 12 | yes | full 2x2 | 1 ppm VCTCXO, ext ref | 3.0 | bladerf | $$$ |
| USRP B200/B205mini | 70 MHz-6 GHz | 56 MS/s (1 ch) | 12 | yes | full 1x1 | 2 ppm (GPSDO opt.) | 3.0 | uhd | $$$$ |
| USRP B210 | 70 MHz-6 GHz | 56 MS/s (61.44 raw) | 12 | yes | full 2x2 | 2 ppm (GPSDO opt.) | 3.0 | uhd | $$$$ |
| USRP N210 / N320 / X310 | per daughterboard, DC-6 GHz | 25 / 200 / 200 MS/s | 14-16 | yes | full | 10 MHz/PPS ext | GigE/10GbE | uhd | $$$$$ |
| KrakenSDR | 24 MHz-1.766 GHz, 5 coherent ch | 2.56 MS/s x5 | 8 | no | - | shared clock | 2.0 | rtlsdr (kraken fork) | $$$ |
| RSP / MSI.SDR clones | as RSP1 | 8 MHz | 12 | no | - | - | 2.0 | sdrplay (older API) | $ |
| Ettus / NI USRP B200mini-i, E310/E320 | 70 MHz-6 GHz, embedded ARM | 56 / 61.44 MS/s | 12 | yes | full | GPSDO opt. | 3.0 / SoC | uhd | $$$$ |
| Ubertooth One | 2.4 GHz only | 1 MHz channels | 8 | yes (BT) | half | - | 2.0 | ubertooth | $$ |
| YARD Stick One | 300-348, 391-464, 782-928 MHz (CC1111) | sub-MHz, packet radio | - | yes | half | - | 2.0 | rfcat | $$ |
| CaribouLite (RPi HAT) | 30 MHz-6 GHz | 4 MS/s | 13 | yes | half | - | SMI | soapy | $$ |
| RFNM | 5 MHz-7.2 GHz | 153.6 MS/s (2 ch) | 12 | yes | full | ext ref | 3.x | rfnm (soapy) | $$$ |
| Antsdr E200 / E310 (Pluto-compatible) | 70 MHz-6 GHz | 61.44 MS/s | 12 | yes | full 2x2 | 0.5 ppm | GigE / 2.0 | plutosdr | $$$ |

Notes: "$" < 60 USD, "$$" 60-350, "$$$" 350-800, "$$$$" 800-2500, "$$$$$" > 2500.

## 2. Device-specific details and quirks

### RTL-SDR (RTL2832U + R820T2 / R828D / E4000 / FC0012)

- The RTL2832U demodulator chip does the ADC (8-bit, 28.8 MHz) and decimates; the tuner sets
  the frequency. Tuner determines range: R820T/R820T2 24-1766 MHz, R828D (V4) same plus the
  V4 board's built-in upconverter for 500 kHz-28.8 MHz, E4000 52-2200 MHz with gap 1100-1250.
- **Direct sampling** (V3): `-D 2` / `direct_samp=2` (Q branch) gives 500 kHz-28.8 MHz real
  sampling at reduced performance; V4 replaces this with an upconverter and needs the
  rtl-sdr-blog driver fork (`librtlsdr` from rtlsdrblog GitHub, or SDR++/SDR# builds that include it).
- Sample rates: 225 001-300 000 or 900 001-3 200 000 S/s. 2.4 MS/s is reliable, 2.56 usually
  fine, 2.88/3.2 drop samples on most hosts.
- Gain: R820T table in dB x10: 0 0.9 1.4 2.7 3.7 7.7 8.7 12.5 14.4 15.7 16.6 19.7 20.7 22.9
  25.4 28.0 29.7 32.8 33.8 36.4 37.2 38.6 40.2 42.1 43.4 43.9 44.5 48.0 49.6. AGC (`-g 0`
  in some tools) is fine for scanning, bad for measurements.
- **Bias tee** (V3/V4, SMArTee): 4.5 V, ~180 mA: `rtl_biast -b 1`, or `-T` in rtl_sdr/rtl_fm/
  rtl_433, `bias_tee=1` in SoapySDR args; only with an LNA attached.
- Heat: V3/V4 in metal cases run warm; TCXO holds ~1 ppm anyway. Generic dongles drift
  tens of ppm in the first 10 minutes; calibrate after warm-up.
- Known issues: USB noise from cheap cables and laptop chargers; strong FM/pager overload
  (add FM notch); 1.5 ppm error swaps 1 kHz at 1 GHz, enough to lose narrowband digital modes.
- Software: `rtl_test -t` (device/tuner check), `rtl_test -p` (ppm drift estimate),
  `rtl_sdr`, `rtl_fm`, `rtl_power`, `rtl_tcp`, `rtl_adsb`, `rtl_eeprom` (serial numbers to
  address multiple dongles: `-d :00000002` or `rtlsdr=serial` in Soapy).

### HackRF One

- MAX2837 transceiver (2.3-2.7 GHz native) + RFFC5072 mixer to cover 1 MHz-6 GHz;
  MAX5864 8-bit ADC/DAC at up to 20 MS/s; CPLD + LPC4320 MCU; USB 2.0.
- Half-duplex: cannot TX and RX at once. Sample rates: 2-20 MS/s (8, 10, 20 common);
  baseband filter (`-b`) options 1.75-28 MHz; leave auto (0.75 x fs).
- Gains: RX LNA 0-40 dB (8 dB steps, `-l`), RX VGA 0-62 dB (2 dB steps, `-g`), amp 14 dB
  (`-a 1`) (avoid near strong signals). TX VGA 0-47 dB (`-x`), TX amp +14 dB. Max TX ~ +15 dBm
  at low bands, lower above 2 GHz.
- Clock: 25 MHz 20 ppm crystal; add the TCXO (0.5 ppm) or feed `CLKIN` 10 MHz 3.3 V square/sine.
  `CLKOUT` lets you sync a second HackRF (still not phase-coherent without extra work).
- Firmware: `hackrf_spiflash -w hackrf_one_usb.bin` and CPLD update per release notes; PortaPack
  (Mayhem firmware) turns it into a standalone device.
- Quirks: 8-bit + wideband front-end = overload from FM/cellular unless you add filters;
  "opera cake" antenna switcher add-on; the hardware has no LNA before the mixer so
  sensitivity is mediocre above 3 GHz (add an external LNA).
- Tools: `hackrf_info`, `hackrf_transfer -r file.cs8 -f 915000000 -s 10000000 -l 32 -g 20`,
  `hackrf_transfer -t file.cs8 -f ... -x 20` (TX), `hackrf_sweep` (fast spectrum sweep 1-6 GHz).

### Airspy R2 / Mini / HF+ Discovery

- R2/Mini: R820T2 tuner + LPC4370 with 12-bit ADC at 20 MS/s decimated to 10/2.5 (R2) or
  6/3 (Mini) MS/s; excellent dynamic range for the price; 0.5 ppm; bias tee 4.5 V.
  Gains: three (LNA/mixer/IF) or "linearity"/"sensitivity" presets (0-21). Use "linearity"
  near strong signals.
- HF+ Discovery: dual-conversion, polyphase harmonic rejection mixer, 18-bit equivalent;
  best affordable HF/VHF-low receiver; only 912 kHz span; no bias tee.
- Tools: `airspy_rx`, `airspy_info`; SoapySDR modules `SoapyAirspy`, `SoapyAirspyHF`;
  SDR# has native support; SDR++ native.

### SDRplay RSP family (RSP1A/1B, RSP2, RSPdx, RSPduo)

- 14-bit ADC via MSi2500/MSi001, 10 MHz max span, 1 kHz-2 GHz continuous, many preselector
  filters (a real advantage over RTL-SDR), 0.5 ppm, bias tee (4.7 V). Closed-source API
  (v3.x) required; Linux needs the vendor `sdrplay_apiService` daemon running.
- RSPduo has two tuners with a common clock: diversity, dual-band, or phase-coherent 2 MHz mode.
- Gains: IF gain reduction (`gRdB` 20-59) and LNA state (`LNAstate` 0-9 depending on band);
  lower gRdB = more gain. Notch filters for FM broadcast and MW/DAB in RSP1A/dx.
- Software: SDRuno (Windows), SDRconnect (cross-platform), SDR++/GQRX/GNU Radio via
  SoapySDRPlay3, SDRangel native. API updates often break SoapySDRPlay3 builds; match versions.

### ADALM-Pluto (PlutoSDR)

- AD9363 transceiver (stock: 325-3800 MHz, 20 MHz BW; "ad9364" unlock via
  `fw_setenv attr_name compatible; fw_setenv attr_val ad9364` -> 70-6000 MHz, 56 MHz BW),
  Zynq 7010 SoC running Linux, USB 2.0 (also acts as Ethernet-over-USB, IP 192.168.2.1),
  12-bit, 61.44 MS/s ADC but USB2 sustains ~4-5 MS/s; second RX/TX channel enabled on rev C/D
  with `fw_setenv mode 2r2t`.
- Connect over `ip:192.168.2.1` (libiio context) or `usb:`; can also be networked via
  a USB Ethernet adapter (`ip:pluto.local`).
- Gain: RX 0-73 dB with modes `manual`, `slow_attack`, `fast_attack`, `hybrid`;
  TX attenuation 0 to -89.75 dB (`hardwaregain` negative), output ~ +7 dBm max at 0 dB.
- Frequency accuracy 25 ppm stock (bad for narrowband); mod the TCXO or feed external clock
  (rev C/D have a clock input pad). `xo_correction` attribute trims ppm in software.
- Software: `pyadi-iio` (Python), `gr-iio` (GNU Radio 3.10 has `iio` blocks built in),
  SoapyPlutoSDR, SDRangel, SDR++ (plutosdr source), MATLAB/Simulink support.
- Quirk: DC offset and IQ imbalance correction is automatic in the AD936x (`quadrature_tracking`,
  `bb_dc_offset_tracking`); disable for TX-loopback measurements.

### LimeSDR / LimeSDR Mini

- LMS7002M transceiver, 12-bit, full-duplex; LimeSDR USB 100 kHz-3.8 GHz 2x2 61.44 MS/s; Mini 2.0
  10 MHz-3.5 GHz 1x1 (30.72 MS/s). LimeSuite (`LimeUtil --find`, `LimeQuickTest`, `LimeSuiteGUI`)
  handles calibration; SoapySDR `lime` driver, `gr-limesdr`.
- Quirks: needs firmware/gateware matching LimeSuite version; RX gain split into LNA/TIA/PGA;
  choose the right RF port (LNAH/LNAL/LNAW by frequency); calibrations must be re-run after
  frequency changes for best IQ balance; runs hot, add a fan/heatsink.

### BladeRF 2.0 micro (xA4/xA9)

- AD9361, 47 MHz-6 GHz, 2x2 full duplex, 61.44 MS/s, USB 3.0, 1 ppm VCTCXO with taming via
  external ref, bias tee on each port, FPGA (xA9 has room for custom DSP). `bladeRF-cli -i`,
  `bladeRF-cli -p` (probe), firmware + FPGA images from Nuand; SoapySDR `bladerf`, `gr-osmosdr`.
- Gains: RX `agc` or manual 0-60 dB (`bladeRF-cli -e "set gain rx1 40"`); TX -24 to +66 dB.
- Quirk: USB 3 controller compatibility (avoid ASMedia older chipsets); use the FPGA
  autoload to skip the 10 s load at open.

### USRP B200 / B210 / B205mini / N-series / X-series

- UHD driver (`uhd_find_devices`, `uhd_usrp_probe`, `rx_samples_to_file`, `uhd_fft`).
  B2x0: AD9361/9364, 70 MHz-6 GHz, 56 MS/s single channel (USB 3.0), 2 ppm TCXO, optional
  GPSDO, external 10 MHz/PPS. Timestamps, `set_start_time`, `rx_time` tags -> best device for
  timing-critical and coherent work.
- Gain: B2x0 RX 0-76 dB (`gain` arg), TX 0-89.8 dB. Set `bandwidth` explicitly.
- N210 (Ethernet, 25 MS/s, 100 MS/s ADC, daughterboards WBX/SBX/CBX/UBX by band) and X310
  (10GbE, 200 MS/s, dual daughterboards) for lab-grade work; RFNoC for FPGA processing.
- Quirks: firmware/FPGA images must match the UHD version (`uhd_images_downloader`);
  `recv_frame_size`/`num_recv_frames` args for USB stability; Windows needs the UHD driver
  bundle and often the USB 3 driver fix.

### KrakenSDR

- Five RTL-SDR channels sharing one clock and a noise-source for calibration -> coherent.
  Direction finding via MUSIC/root-MUSIC in the Kraken web UI (Raspberry Pi 4/5), also passive
  radar experiments. 24 MHz-1.766 GHz, 2.56 MS/s per channel, requires 5-element antenna array
  (UCA or ULA) spaced 0.1-0.5 lambda.

## 3. Front-end accessories

| Item | Purpose | Notes |
|---|---|---|
| Wideband LNA (SPF5189Z, PGA-103, LNA4ALL, Nooelec SAWbird) | Lower system NF, compensate coax | Put at the antenna, power via bias tee; SAWbird = LNA + SAW filter for one band (137 MHz, 1090, 1420, 1575, 1690) |
| FM broadcast notch (88-108 MHz) | Stop overload of RTL-SDR/HackRF | Essential in cities |
| Band-pass filters (ADS-B 1090, GPS 1575, NOAA 137) | Reject out-of-band | Improves decode rate more than more gain |
| Low-pass/high-pass (HF LPF 30 MHz) | Direct-sampling / upconverter cleanliness | |
| Upconverter (Ham It Up, SpyVerter) | HF on VHF-only SDRs | 125 MHz LO (Ham It Up) or 120 MHz (SpyVerter); tune fc + LO |
| Attenuators (fixed 10/20/30 dB SMA, step) | Overload, lab cabling | Never TX into an SDR without >=30 dB attenuation |
| Bias tee (external) | Power LNA over coax | 5-12 V; check LNA voltage |
| Dummy load 50 ohm | Safe TX testing | Rated for your power |
| Reference clock / GPSDO (Leo Bodnar, u-blox + DA) | ppm accuracy, coherence | 10 MHz into CLKIN / REF IN |
| Coax: RG-58, RG-6 (75 ohm, fine for RX), LMR-240/400 | Feedline | Loss/100 m at 1 GHz: RG-58 ~50 dB, RG-6 ~20 dB, LMR-400 ~13 dB |
| Adapters SMA/N/BNC/F/MCX/TS9 | | RTL-SDR/HackRF/Airspy/Pluto/Lime: SMA female; generic dongles: MCX; BladeRF: SMA; RSP: SMA (RSPdx also BNC) |
| USB hub (powered) / good cable | Reliability | Many "device not found" reports are cables |
| ESD protection / gas discharge tube | Antenna safety | Ground the mast, disconnect in storms |

## 4. Choosing by use case

| Use case | Minimum | Better |
|---|---|---|
| ADS-B, AIS, POCSAG, FM, airband, NOAA APT | RTL-SDR V3/V4 + filtered LNA | Airspy Mini |
| HF listening / digital modes (FT8, WSPR) | RTL-SDR V4 or V3 direct sampling | Airspy HF+ Discovery, RSP1B |
| Wideband scanning, trunked systems (needs >=8 MHz) | Airspy R2 / RSPdx | two SDRs, or BladeRF |
| GSM/LTE cell scanning (RX) | RTL-SDR (single 200 kHz channel) | USRP B2x0/LimeSDR for full 20 MHz |
| Reverse engineering key fobs / IoT (RX) | RTL-SDR + URH | HackRF for replay in the lab |
| LoRa research (RX/TX) | RTL-SDR RX only | Pluto / LimeSDR / USRP for TX |
| Satellite L-band (GOES, Inmarsat, Iridium) | RTL-SDR + SAWbird + dish/patch | Airspy/USRP for Iridium bursts |
| Passive radar / DF | KrakenSDR | USRP B210 / N3xx with shared clock |
| Full-duplex protocol emulation (GSM BTS lab, LTE eNB) | LimeSDR Mini / Pluto | USRP B210 with GPSDO |
| Bluetooth / 2.4 GHz FHSS | Ubertooth (BT only) | USRP/BladeRF 40+ MHz bandwidth |
| 24 GHz, 60 GHz, radar | none of the above | mmWave front-ends with a 6 GHz SDR as IF |

## 5. Enumerating devices quickly

```
rtl_test -t                      # RTL-SDR present? tuner type? sample rate test
hackrf_info                      # HackRF serial, firmware, board rev
airspy_info                      # Airspy
SoapySDRUtil --find              # every device with a Soapy module installed
SoapySDRUtil --probe="driver=rtlsdr"   # gains, rates, antennas, args
uhd_find_devices ; uhd_usrp_probe      # USRP
iio_info -s ; iio_info -u ip:192.168.2.1 | head    # Pluto
LimeUtil --find ; bladeRF-cli -p       # Lime / BladeRF
```

`scripts/probe_devices.py` runs all of these and summarizes.

## 6. Multi-device and coherence

- Two independent SDRs are not phase-coherent even with a shared 10 MHz reference; sample
  clocks and LO phases differ. Coherent options: KrakenSDR, RSPduo, USRP B210 (two channels
  on one AD9361), LimeSDR/BladeRF 2x2, or multiple USRPs with 10 MHz + PPS + `set_time_unknown_pps`
  and a phase calibration with a splitter and a reference signal.
- Multiple RTL-SDRs: address by serial (`rtl_eeprom -s 00000101` to set), each on its own
  USB2 bandwidth budget (~3 x 2.4 MS/s per USB2 controller in practice).
