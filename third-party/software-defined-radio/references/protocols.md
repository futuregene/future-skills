# Protocol Decoding Catalog

For each: frequency, modulation, symbol/bit rate, minimum sample rate, the tool and an exact
command, and a legal note. **Frequencies are ITU Region defaults; confirm your country's
band plan.** Receiving broadcast, aviation, maritime, amateur, and unencrypted telemetry is
legal in most places; some countries restrict decoding/logging or forbid divulging contents.
Cellular voice/data and encrypted public-safety traffic are off-limits.

## Aviation

### ADS-B (1090 MHz Extended Squitter)
- 1090 MHz, PPM (pulse position), 1 Mbps, 2 MS/s minimum. Gain high (40-49), 1090 MHz band-pass
  + LNA helps a lot.
```bash
dump1090-fa --device-type rtlsdr --gain 40 --net --write-json /run/dump1090-fa
# view at http://localhost:8080 (tar1090). readsb is the higher-performance fork.
```
Legal: universally receivable; it is an unencrypted broadcast for collision avoidance.

### UAT 978 MHz (US, weather + position for GA)
- 978 MHz, CPFSK, 1.04 Mbps, 2.083 MS/s. `dump978-fa --sdr driver=rtlsdr | ...`.

### ACARS (VHF datalink, aircraft ops messages)
- 131.550 (US primary), 131.725/131.825 (EU), NBFM+MSK 2400 bps, 24 kS/s per channel.
```bash
acarsdec -r 0 131.550 131.725 131.825           # -r = rtlsdr index; feed acarshub for a web UI
```
### VDL Mode 2 (2010s+ ACARS successor)
- 136.650-136.975, D8PSK 10.5 kbaud. `dumpvdl2 --rtlsdr 0 136975000 136725000`.
### HF ACARS / SATCOM (Inmarsat AERO)
- Inmarsat L-band 1545 MHz region; `JAERO` from an SSB/IQ feed. HFDL: `dumphfdl`.

## Maritime

### AIS (ship positions)
- 161.975 (ch 87B) + 162.025 (ch 88B) MHz, GMSK 9600 bps, 25 kHz channels; capture both with
  ~48-96 kS/s each or one wideband capture.
```bash
AIS-catcher -d 0 -v                      # RTL-SDR, decodes both channels; -N 8100 for web UI
# or: rtl_ais -n            (NMEA on UDP 10110)
```
Legal: AIS is an open safety broadcast; OpenCPN plots it.

### NAVTEX (518 kHz maritime safety text)
- 518 kHz (also 490, 4209.5), FSK 100 baud 170 Hz shift, USB audio into fldigi/YaND.

## Pagers and simple data

### POCSAG / FLEX
- Common on 137-138, 148-150, 152-159, 280-284, 929-932 MHz (region-dependent), 2FSK direct.
```bash
rtl_fm -f 148.5M -M fm -s 22050 -g 30 - | multimon-ng -t raw -a POCSAG512 -a POCSAG1200 -a POCSAG2400 -a FLEX -f alpha /dev/stdin
```
Legal: **pager content is often private (medical, personal). Many jurisdictions forbid
decoding, logging, or divulging it.** Treat as read-only lab curiosity; do not publish contents.

### rtl_433 ISM sensors (the workhorse)
- 433.92 / 315 / 868.3 / 915 MHz, mostly OOK/ASK and 2FSK; 250 kS/s.
```bash
rtl_433 -f 433.92M -f 868.3M -f 915M -H 30s -s 250k -F json -M level -M time:iso
rtl_433 -A                              # pulse analyzer for a new/unknown device
rtl_433 -R 0 -X 'n=my,m=OOK_PWM,s=500,l=1000,r=6000,g=800,t=0,y=0'   # flex decoder for custom OOK
```
Decodes weather stations, TPMS, remote thermometers, energy meters, door/window sensors,
soil moisture, some 433 remotes. Legal: receiving your own/neighbourhood sensors is fine;
respect privacy for anything personal.

### wM-Bus utility meters
- 868.95 MHz (T/C mode), 169 MHz (N mode). `rtl_wmbus` or `wmbusmeters --device=rtlwmbus:...`.

## Amateur / experimenter modes

### APRS (packet position/telemetry, 2 m)
- 144.390 (US), 144.800 (EU/ID region), 145.575, AFSK1200 Bell 202 in NBFM.
```bash
rtl_fm -f 144.800M -M fm -s 24000 -g 30 - | direwolf -c direwolf.conf -r 24000 -B 1200 -
# or feed 48 kHz audio to direwolf; it also does IGate to APRS-IS
```
### FT8 / FT4 / WSPR / JT65 (weak-signal HF)
- HF band segments (e.g. 14.074 MHz FT8 USB dial), narrow FSK, decode in WSJT-X from SSB audio
  (route GQRX/SDR++ audio to WSJT-X via VB-Cable/PulseAudio loopback). WSPR TX is amateur-licensed.
### PSK31 / RTTY / Olivia
- HF, into fldigi from USB audio.
### SSTV
- 14.230 MHz (HF), 145.800 (ISS downlink), decode with QSSTV/MMSSTV from FM/SSB audio.

## Digital voice and trunking

### DMR / P25 / NXDN / D-STAR / YSF (conventional and trunked)
- VHF/UHF business/public-safety allocations, 4FSK/C4FM/GMSK 4800 baud (DMR/P25/NXDN), 12.5/6.25 kHz.
```bash
# SDRTrunk (GUI, best for trunking): configure the SDR, add the system's control channel
# CLI: rtl_fm -f 461.0375M -M fm -s 24000 -g 35 - | dsd-fme -i - -o /dev/null -fr   (DMR)
```
Legal: **Decoding voice may be restricted; encrypted public-safety must not be decrypted, and
decryption tooling is out of scope.** Unencrypted amateur digital voice (D-STAR/DMR on ham
bands) is fine. Know your country's monitoring laws.

### TETRA
- 380-430 MHz (public safety) / 806-870, pi/4-DQPSK 18 kbaud. `tetra-kit` / `osmo-tetra` (research);
  encrypted networks are not decodable and are off-limits.

## Satellites

### NOAA APT (137 MHz weather images)
- 137.100 (NOAA-19), 137.9125 (NOAA-15), 137.620 (NOAA-18), WBFM ~34 kHz deviation, AM subcarrier.
```bash
satdump live noaa_apt out --source rtlsdr --samplerate 1.024e6 --frequency 137.1e6 --gain 45
# or record IQ during the pass and: satdump noaa_apt baseband cap.wav out --samplerate ... --baseband_format ...
```
Antenna: V-dipole or QFH for 137 MHz; track with gpredict/Look4Sat.

### Meteor-M N2/N2-x LRPT (137 MHz digital weather images)
- 137.100 / 137.900, QPSK/OQPSK 72 or 80 ksym/s. SatDump `meteor_m2-x_lrpt` pipeline.

### GOES / GK-2A / Elektro-L / FengYun HRIT/LRIT (geostationary, L-band ~1.69 GHz)
- BPSK; needs a dish (or big grid) + 1.69 GHz LNA (SAWbird GOES) + RTL-SDR/Airspy.
  `satdump live goes_hrit ...` or `goestools`.

### Iridium (1616-1626 MHz bursts)
- QPSK bursts; wideband capture (Airspy/HackRF), `gr-iridium` -> `iridium-toolkit` (frame stats,
  some unencrypted broadcast/ring-alert info only). Legal: do not attempt to decode private traffic.

### Inmarsat STD-C / AERO (~1537-1545 MHz)
- BPSK; `scytale-c` (STD-C EGC safety broadcasts) or `JAERO` (AERO). EGC is public safety info.

### Cubesats / weather-sonde beacons
- `gr-satellites` has hundreds of decoders keyed by NORAD ID; feed IQ or audio; outputs telemetry/KISS.

### Radiosondes (weather balloons, 400-406 MHz)
- RS41/RS92/DFM/M10/M20, GFSK 4800 bd. `radiosonde_auto_rx` autoscans, decodes, and maps.

## ISM / IoT / short range

### LoRa
- EU 868, US 915, ID 920-923 MHz, CSS SF7-12, BW 125/250/500 kHz.
```bash
# gr-lora_sdr flowgraph (Tapparel) does full RX; parameters: sf, bw, cr, sync word, has_crc, impl_head
# quick sniff of your own node's uplinks; LoRaWAN payloads are AES-encrypted (you need the keys you own)
```
Legal: receive your own devices; LoRaWAN app payloads are encrypted end to end.

### Zigbee / 802.15.4 (2.4 GHz, and 868/915)
- OQPSK-DSSS 250 kbps, 2 MHz channels (11-26). `gr-ieee802-15-4`, or a dedicated sniffer
  (nRF/CC2531 + Wireshark) is easier than SDR.

### Bluetooth / BLE (2.4 GHz FHSS)
- GFSK 1 Mbps; hopping makes SDR hard. Use Ubertooth (`ubertooth-btle`) or
  `ice9-bluetooth-sniffer` with a wideband SDR (>= 40 MHz, USRP/BladeRF).

### TPMS (tire pressure, 315/433 MHz)
- FSK/OOK, many vendor formats; `rtl_433 -f 315M` and `-f 433.92M`. Legal: your own car is fine.

## Broadcast and navigation

### FM broadcast + RDS
- 87.5-108 MHz WBFM; RDS at 57 kHz. `redsea` (`rtl_fm ... | redsea`) or SDR++/SDRangel RDS.
### DAB+ (Band III ~174-240 MHz)
- OFDM. `welle.io` (GUI) with RTL-SDR/Airspy.
### DVB-T / DVB-S
- OFDM / QPSK. Use the dongle in DVB mode (`w_scan`, TV apps) for DVB-T; `leandvb`/`gr-dvbs2rx`
  for DVB-S/S2 with a dish + LNB + bias-tee-fed downconverter.
### GNSS (GPS/GLONASS/Galileo/BeiDou, ~1.575/1.602/1.207 GHz)
- BPSK DSSS below noise; `GNSS-SDR` with an active GPS antenna + bias tee + 1575 MHz filter.
  Position fix from raw IQ; also a good SDR sanity/timing test.

## Cellular (RX / research only)

### GSM (900/1800 downlink)
```bash
kal -s GSM900 -g 40           # find strong ARFCNs and measure ppm error
grgsm_livemon -f 947.4M -g 40 # live BCCH; grgsm_scanner for a survey
# gr-gsm outputs GSMTAP to loopback; Wireshark decodes system-information (broadcast) messages
```
Legal: **only unencrypted broadcast/system-information is analyzed; user voice/SMS is
encrypted and private. Do not attempt to decrypt or capture subscriber traffic. Operating a
BTS/eNB is only legal in a shielded lab with your own SIMs and, where required, a test license.**

### LTE / 5G (RX)
- `LTE-Cell-Scanner`/`CellSearch` (find cells, MIB/SIB broadcast), `srsRAN` (full stack, needs
  full-duplex SDR + shielded lab for any TX). Analyze only broadcast channels off the air.

## Workflow for a protocol not listed here

1. Identify frequency, modulation, symbol rate (`signal-identification.md`, `symbol_rate.py`).
2. Search: "<device/system name> rtl_433" / "gr-<name>" / "<name> SDR decode" / sigidwiki.
3. If a decoder exists, use it. If not, demodulate to a bitstream (URH/GNU Radio), find the
   preamble/sync/length/CRC, and write a small parser.
4. Validate against a capture where you know the ground truth (your own device sending known data).
5. Record captures as SigMF so others can reproduce.
