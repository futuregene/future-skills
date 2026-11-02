# SDR Software Toolchain

Drivers, receivers, analyzers, decoders, and install recipes per operating system.
Versions move; commands below are stable across recent releases (2024-2026).

## 1. Driver layer (what talks to the hardware)

| Layer | Provides | Installed as |
|---|---|---|
| librtlsdr (osmocom) / rtl-sdr-blog fork | `rtl_sdr`, `rtl_fm`, `rtl_tcp`, `rtl_test`, `rtl_power`, `rtl_biast` | `apt install rtl-sdr`, `brew install librtlsdr`, Windows zip from rtl-sdr.com; V4 needs the blog fork |
| libhackrf | `hackrf_info`, `hackrf_transfer`, `hackrf_sweep`, `hackrf_spiflash` | `apt install hackrf`, `brew install hackrf`, Windows release zip / PothosSDR |
| libairspy / libairspyhf | `airspy_rx`, `airspy_info` | `apt install airspy`, brew |
| SDRplay API 3.x | `sdrplay_apiService` daemon + headers | vendor installer only (sdrplay.com) |
| libiio + libad9361 | Pluto/ADI access (`iio_info`, `iio_attr`) | `apt install libiio-utils`, ADI Windows installer |
| UHD | USRP (`uhd_find_devices`, `uhd_fft`, `rx_samples_to_file`) | `apt install uhd-host`, `pip install uhd`? no: use conda/radioconda or Ettus binaries; run `uhd_images_downloader` |
| LimeSuite / bladeRF | `LimeUtil`, `bladeRF-cli` | PPA/brew/vendor |
| **SoapySDR** | Vendor-neutral C++/Python API + `SoapySDRUtil`; modules: SoapyRTLSDR, SoapyHackRF, SoapyAirspy, SoapyAirspyHF, SoapySDRPlay3, SoapyPlutoSDR, SoapyUHD, SoapyLMS7, SoapyBladeRF, SoapyRemote, SoapyAudio | `apt install soapysdr-tools soapysdr-module-all`, brew, PothosSDR (Windows), conda-forge |
| gr-osmosdr | GNU Radio source/sink block wrapping rtl/hackrf/airspy/bladerf/uhd/soapy | `apt install gr-osmosdr`; GNU Radio 3.10 also ships native `Soapy` and `UHD` and `IIO` blocks (prefer these) |

Windows USB driver: **Zadig** (zadig.akeo.ie) -> Options > List All Devices -> select
`Bulk-In, Interface (Interface 0)` (RTL-SDR) or `HackRF One` -> WinUSB -> Replace Driver.
Linux: udev rules (`/etc/udev/rules.d/`, shipped by packages; log out/in or `udevadm control
--reload`), and blacklist the DVB kernel driver for RTL-SDR:

```
echo "blacklist dvb_usb_rtl28xxu" | sudo tee /etc/modprobe.d/blacklist-rtl.conf
sudo modprobe -r dvb_usb_rtl28xxu
```

## 2. General receivers (GUI)

| App | OS | Strengths | Sources |
|---|---|---|---|
| **SDR++** | Win/Linux/mac/Android | Fast, clean, plugin modules (rtl, hackrf, airspy, sdrplay, pluto, soapy, spyserver, rtl_tcp, file), recorder with metadata WAV, decoders (RDS, meteor demod, pager) | all |
| **SDRangel** | Win/Linux/mac/Android | Huge feature set: many demods (DMR/dPMR/YSF/D-STAR via DSDcc, ADS-B map, AIS, APRS, ATV, DAB, DVB-S, FT8, radiosonde, satellite tracker, TX plugins), REST API | all |
| **GQRX** | Linux/mac | Simple, scriptable via remote TCP port 7356 (rigctl protocol), UDP audio out to decoders | gr-osmosdr / Soapy |
| **SDR#** (SDRSharp) | Windows | Plugin ecosystem (DSD+, Frequency Manager, IF recorder, co-channel canceller), Airspy native | rtl, airspy, spyserver, plugins |
| **SDRconnect / SDRuno** | Win/Linux/mac | SDRplay official | SDRplay only |
| **CubicSDR** | all | Soapy-based, straightforward | Soapy |
| **HDSDR** | Windows | ExtIO DLL model, classic HF | ExtIO |
| **Satdump** | all | Satellite imaging pipelines with live recording | rtl/airspy/hackrf/pluto/soapy |
| **OpenWebRX+ / KiwiSDR / WebSDR** | Linux server | Multi-user web receiver with built-in digital decoders | rtl/airspy/sdrplay/soapy |

## 3. DSP frameworks

- **GNU Radio 3.10.x** (stable, C++/Python, GRC editor). 3.8 (Python 3, legacy) still found in
  older tutorials; block names changed (e.g. `WX GUI` gone, `QT GUI` only; `Clock Recovery MM`
  superseded by `Symbol Sync`). 3.11/4.0 are the next generation; expect block-API changes.
  See `gnuradio.md`.
- **Pothos / PothosSDR** (Windows bundle that also ships SoapySDR, GQRX, CubicSDR, GNU Radio).
- **LuaRadio**, **FutureSDR** (Rust), **redhawk**, **MATLAB/Simulink Communications Toolbox**
  (Pluto/RTL-SDR/USRP support packages), **GNSS-SDR** (full GNSS receiver on GNU Radio/Volk).
- **Python**: numpy/scipy + SoapySDR/pyrtlsdr/pyadi-iio/uhd; `sigmf`; `scipy.signal` for filters;
  `commpy`, `pyphysim` for modem building blocks; `pyqtgraph` for fast live plots.
  See `python-sdr.md`.

## 4. Analysis and reverse-engineering

| Tool | Use |
|---|---|
| **Universal Radio Hacker (URH)** | Record, view, auto-detect modulation/parameters (bit length, center), demod to bits, protocol field analysis, replay via device; supports rtl/hackrf/airspy/lime/pluto/usrp/soapy |
| **inspectrum** | Waterfall + cursor-based symbol extraction (draw symbol grid, export samples/symbols), reads cu8/cs8/cs16/cf32/wav/sigmf |
| **SigDigger** | Real-time inspection, symbol/ASK/PSK/FSK inspectors, live cursors |
| **Baudline** | Classic spectrum analyzer for audio-rate signals |
| **Audacity / Sonic Visualiser** | Audio-rate captures, AFSK, SSTV |
| **rtl_433 -A** | Pulse analyzer: guesses OOK/FSK encoding from bursts |
| **gr-fosphor** | GPU real-time spectrum/persistence display in GNU Radio |
| **SigMF tools** (`sigmf` Python, `sigmf-converter`) | Metadata and format conversion |
| **Wireshark** | Decoded packets from gr-gsm, gr-ieee802-11/15-4, Ubertooth, srsRAN via pcap/UDP |

## 5. Decoders by domain (see `protocols.md` for parameters)

| Domain | Tools |
|---|---|
| Aviation | dump1090-fa, readsb, dump978-fa (UAT), acarsdec, vdlm2dec/dumpvdl2, acarshub, tar1090 (web UI), JAERO (Inmarsat ACARS), SDRangel ADS-B |
| Maritime | AIS-catcher (best RTL-SDR AIS), rtl-ais, gnuais, OpenCPN (chart display), navtex via fldigi/YaND |
| Pagers | multimon-ng (POCSAG/FLEX/EAS/AFSK/etc.), PDW (Windows), SDRangel pager demod |
| Amateur digital | WSJT-X (FT8/FT4/WSPR/JT65), fldigi (PSK31/RTTY/Olivia/etc.), direwolf (APRS/AX.25 TNC), Xastir/YAAC/APRSIS32, QSSTV/MMSSTV, js8call |
| Digital voice | SDRTrunk (P25/DMR/NXDN/LTR trunking, best all-in-one), DSD-FME / DSDPlus (DMR/P25/NXDN/dPMR/D-STAR/ProVoice), OP25 (P25 Phase 1/2), SDRangel DSDcc, tetra-kit / osmo-tetra (TETRA, research), mbelib (vocoder, patent notes) |
| ISM / IoT | rtl_433 (200+ device protocols), URH, gr-lora_sdr, LoRa-SDR, gr-ieee802-15-4 (Zigbee), Ubertooth/ice9-bluetooth-sniffer/gr-bluetooth, Sigfox-SDR, WMBusMeters (868 MHz utility meters via rtl_wmbus) |
| Satellites | SatDump (NOAA, Meteor, GOES/GK-2A/FY, Elektro-L, MetOp, Iridium, Inmarsat, Orbcomm, many more), gr-satellites (cubesat telemetry decoders), gpredict/Look4Sat/SatNOGS (tracking + rotator), noaa-apt, goestools, JAERO (Inmarsat AERO), gr-iridium + iridium-toolkit, ORBCOMM decoders, scytale-c (Inmarsat STD-C), tinygs |
| Cellular (RX/research) | gr-gsm (grgsm_scanner, grgsm_livemon), kalibrate-rtl (`kal -s GSM900` for ppm), LTE-Cell-Scanner, srsRAN (needs full-duplex SDR), openLTE, osmocom stack (lab BTS with own SIMs), pycrate, 5G: ng-scope research code |
| Broadcast | welle.io (DAB+), gr-dab, leandvb/leansdr (DVB-S), w_scan/dvblast with DVB-T dongles (in DVB mode), gr-dvbt, dream (DRM), gr-rds/redsea (RDS), FMSuite |
| Time / navigation | GNSS-SDR, gnss-sdr-monitor, GPS via `gps-sdr-sim` (TX simulation, lab only), `dcf77`/`wwvb` audio decoders in fldigi/ multimon |
| Weather sondes | radiosonde_auto_rx (RS41/RS92/DFM/M10/M20/iMet), dxlAPRS, SondeMonitor |
| Trunking control | SDRTrunk, trunk-recorder (records all calls of a trunked system), OP25 |
| Wi-Fi | gr-ieee802-11 (802.11a/g/p OFDM TX/RX in GNU Radio), otherwise a Wi-Fi card in monitor mode is the tool, not SDR |
| Spectrum monitoring | rtl_power + heatmap.py, hackrf_sweep + QSpectrumAnalyzer, SDRangel spectrum markers, soapy_power, gr-fosphor, RFExplorer-style scripts |

## 6. Servers and remote SDR

| Server | Client | Notes |
|---|---|---|
| `rtl_tcp -a 0.0.0.0 -p 1234 -s 2400000 -f 100e6` | SDR++, SDR#, GQRX (`rtl_tcp=host:1234`), Soapy `driver=rtltcp` | uncompressed 8-bit, 4.8 MB/s at 2.4 MS/s; LAN only |
| SoapyRemote (`SoapySDRServer --bind`) | any Soapy app with `driver=remote,remote=tcp://host:55132` | any hardware, any format |
| SpyServer (Airspy) | SDR#, SDR++ | compresses, multi-client, IQ/FFT streams |
| OpenWebRX+ | browser | multi-user, demods in the browser, built-in digital decoders |
| SDRangel server mode / REST | remote instances | scripting |
| gr `ZMQ` / `UDP` sink-source | GNU Radio to anything | lab pipelines |
| KiwiSDR / WebSDR public receivers | browser | listen to HF worldwide (rx.linkfanel.net, websdr.org) |

## 7. Install recipes

### Ubuntu / Debian (24.04 tested)

```bash
sudo apt update
sudo apt install -y rtl-sdr hackrf airspy soapysdr-tools soapysdr-module-all \
    gnuradio gr-osmosdr gqrx-sdr inspectrum multimon-ng direwolf rtl-433 \
    libiio-utils uhd-host sox
sudo uhd_images_downloader                      # USRP FPGA images
# newer GNU Radio: PPA
sudo add-apt-repository ppa:gnuradio/gnuradio-releases && sudo apt update && sudo apt install gnuradio
# SDR++: download .deb from github.com/AlexandreRouma/SDRPlusPlus releases
# SatDump, SDRangel: release .deb / AppImage / Flatpak
# URH: pipx install urh   (or pip install urh in a venv)
# dump1090-fa / readsb: FlightAware repo or build from source; AIS-catcher: build from source or release binaries
```

Groups/permissions: `sudo usermod -aG plugdev,dialout $USER` and re-login.

### Fedora / Arch

- Fedora: `dnf install rtl-sdr hackrf gnuradio gr-osmosdr SoapySDR gqrx`.
- Arch: `pacman -S rtl-sdr hackrf gnuradio gnuradio-osmosdr soapysdr soapyrtlsdr gqrx`; AUR for sdrpp, satdump, urh.

### macOS

```bash
brew install librtlsdr hackrf airspy soapysdr soapyrtlsdr soapyhackrf gnuradio gqrx sox
# SDR++ / SDRangel / SatDump: .dmg from releases; RTL-SDR V4: brew install --HEAD librtlsdr (blog fork) or use SDR++ bundled driver
```
Apple Silicon: use native arm64 builds; radioconda works on arm64.

### Windows

1. Drivers: Zadig for RTL-SDR/HackRF (see section 1). SDRplay: vendor API installer.
2. Easiest all-in-one: **radioconda** (GNU Radio + SoapySDR + all modules + gr-osmosdr + Python)
   or **PothosSDR** installer (GNU Radio, GQRX, CubicSDR, inspectrum, URH-ish tools).
3. Receivers: SDR++ (portable zip), SDR# (airspy.com; run `install-rtlsdr.bat`), SDRangel,
   SatDump, HDSDR, SDRuno.
4. Decoders: rtl_433 release zip (`rtl_433.exe`), dump1090 builds, DSD-FME, PDW, SDRTrunk (needs Java 17+),
   URH via `pip install urh` or the installer, WSJT-X, fldigi, direwolf (Windows build).
5. Python: `pip install numpy scipy matplotlib pyrtlsdr sigmf`; SoapySDR Python bindings come
   from radioconda/PothosSDR (add its `bin` to PATH).
6. WSL2: USB passthrough with `usbipd-win` (`usbipd bind --busid X-Y; usbipd attach --wsl --busid X-Y`),
   then Linux tools work inside WSL; GUI via WSLg.

### Docker

- `ghcr.io` images exist for OpenWebRX+, SatDump, gnuradio (git-artes/docker-gnuradio), dump1090/readsb,
  AIS-catcher, rtl_433, SDRangel headless. Pass devices with `--device=/dev/bus/usb` (Linux only) and
  `--privileged` if udev is an issue; on Windows/mac use `rtl_tcp`/SoapyRemote from the host instead.

### Raspberry Pi

- Pi 4/5 handle RTL-SDR decoders (dump1090, AIS-catcher, rtl_433, radiosonde_auto_rx, SatDump
  live) fine; GNU Radio at >= 2 MS/s with GUI is marginal on Pi 4, OK on Pi 5. Use
  `piaware`/`readsb` images for ADS-B feeders, DragonOS Pi for a preinstalled SDR OS.
- Power: RTL-SDR + LNA + Pi on one supply needs >= 3 A; undervoltage causes dropped samples.

### Preinstalled distros

**DragonOS** (Ubuntu-based, most SDR tools preinstalled, x86 + Pi), **Pentoo**, **Kali** (includes
rtl-sdr, hackrf, gnuradio, gr-gsm, URH, inspectrum), **SkyWater/Andrea's SDR images** for Pi.

## 8. Choosing the tool for the task (decision rules)

- "I want to listen / look at the band": SDR++ (all OS); SDRangel if you want built-in digital demods.
- "I want a map of aircraft/ships": dump1090-fa + tar1090; AIS-catcher web UI.
- "I have a mystery signal": record with SDR++ (WAV with metadata) or `rtl_sdr`; open in URH/inspectrum.
- "I want to build a demodulator": GNU Radio (GRC) first, then Python if you need custom logic.
- "I want scripting and automation": Python + SoapySDR (portable) or the device CLI tools piped into decoders.
- "I want many decoders on a headless box": OpenWebRX+ or SDRangel headless + Docker.
- "I need TX": GNU Radio or the device CLI (`hackrf_transfer -t`, `uhd` `tx_samples_from_file`,
  `iio` / pyadi-iio for Pluto); confirm legality first.
