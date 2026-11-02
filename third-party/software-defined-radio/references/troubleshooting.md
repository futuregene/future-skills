# SDR Troubleshooting

Ordered by how often each is the real cause. Start at the top.

## 1. Device not detected

**RTL-SDR**
- Windows: run **Zadig**, Options -> List All Devices, select `Bulk-In, Interface (Interface 0)`
  (for a dual-tuner or RTL-SDR it may be `RTL2838UHIDIR` or `Bulk-In, Interface 0`), install
  **WinUSB**. If you have two interfaces, install on Interface 0. Do not install on your keyboard/mouse.
- Linux: blacklist the DVB driver, unplug/replug:
  ```
  echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-rtl.conf
  sudo modprobe -r dvb_usb_rtl28xxu ; sudo modprobe -r rtl2832 2>/dev/null
  ```
  Check udev rules (`/etc/udev/rules.d/`); add yourself to `plugdev` and re-login.
- `rtl_test -t` should list the tuner. "usb_claim_interface error -6" = the DVB driver still holds
  it (blacklist) or another app is using it (close SDR#/GQRX).
- Try another cable and a direct USB port (not a hub). Cheap cables cause most "no device" reports.
- V4 dongle: you need the **rtl-sdr-blog** driver fork; the old osmocom `librtlsdr` shows no device
  or wrong HF behavior.

**HackRF**: `hackrf_info` should show serial + firmware. If not: Zadig (WinUSB on "HackRF One"),
update firmware (`hackrf_spiflash`), try USB2 port. "Resource busy" = another app open.

**SDRplay**: the `sdrplay_apiService` daemon must be running (Linux) / the API service installed
(Windows). SoapySDRPlay3 must match the installed API version.

**Pluto**: appears as USB Ethernet (192.168.2.1) + mass storage + serial. `iio_info -u ip:192.168.2.1`.
If only mass storage shows, install the Windows drivers or the `libiio`/`libad9361` package.

**USRP**: `uhd_find_devices`; if firmware/FPGA mismatch, run `uhd_images_downloader`. USB3 devices
need a USB3 port and sometimes `num_recv_frames`/`recv_frame_size` tuning.

**Generic**: `SoapySDRUtil --find` shows everything with a Soapy module; if your device is missing,
the Soapy module isn't installed.

## 2. Overruns / underruns / dropped samples (`O`, `U`, `D`, `S`, stuttering audio)

- **Lower the sample rate.** 2.4 MS/s is the RTL-SDR ceiling; 3.2 drops samples. HackRF: use 8-10
  MS/s, not 20, unless you need it.
- **Decimate immediately** after the source; don't run wideband through GUI sinks.
- **USB**: USB3 device on a USB2 port, or through a hub, starves. Use a direct USB3 port and short
  cable. Don't share a USB2 controller among several dongles above ~3x 2.4 MS/s total.
- **CPU**: close other apps; set the CPU governor to performance; run `volk_profile` once
  (GNU Radio). Reduce FFT size / update rate of waterfall displays.
- **Disk**: recording high rates to a slow disk causes `O`. cf32 at 20 MS/s = 160 MB/s; use an SSD
  or a smaller format (cs8/cu8) and lower rate.
- **Pluto/USB2**: sustained rate caps ~4-5 MS/s; raise `rx_buffer_size` (2^16-2^18).

## 3. Signal at the wrong frequency (ppm / calibration)

- Cheap dongles drift 20-60 ppm, worse when cold. TCXO models ~0.5-1 ppm.
- Measure with a known signal: an FM broadcast pilot, a strong local repeater, or
  `kal -s GSM900` then `kal -c <ch>` which prints the ppm error. `rtl_test -p` estimates drift.
- Apply the correction: `-p <ppm>` in rtl tools, "Frequency correction" in the GUI, `set_freq_corr`
  in code. Recheck after 10 minutes of warm-up.
- Narrowband digital (POCSAG, DMR, LoRa SF12, FT8) fails without ppm correction; wideband FM does not care.

## 4. Big spike at the center frequency (DC offset)

- Cause: LO leakage + ADC DC offset; always present at exactly `fc`.
- Fix: tune 100-500 kHz to the side of your target and shift back in software (`Frequency Xlating
  FIR`, or `x*exp(-j2pi f_off n/fs)`); enable "offset tuning" on E4000 tuners; apply a DC blocker.
- In GUIs: "Offset tuning" / "DC removal" / "DC blocker" checkboxes.

## 5. Mirror image of a signal (IQ imbalance)

- A weaker mirror at `-f` relative to a strong signal, symmetric about `fc`.
- Fix: enable "IQ correction"/"IQ balance" (auto in Pluto/USRP; software in SDR#/SDR++/GNU Radio
  `IQ Balance`); lower gain; it is not a real signal (disconnect antenna to confirm it stays for
  internal spurs but the image tracks the real signal).

## 6. Whole band full of ghosts / many evenly spaced "stations" (overload, intermod)

- Front-end overload from a strong nearby transmitter (FM broadcast, pager, cell, your own TX).
- Fix: **reduce gain 10-20 dB** (the fastest test: ghosts vanish); add an **FM broadcast notch**
  (88-108 MHz) and/or a band-pass filter for your target; turn off the extra amp/AGC; move away
  from the strong source. RTL-SDR and HackRF (8-bit, weak front ends) overload easily; SDRplay/
  Airspy tolerate more.

## 7. Nothing but noise (no signal)

Check in this order:
1. Antenna actually connected, right connector, coax not open/shorted.
2. Right frequency and enough `fs` to contain the signal; verify with a known strong signal
   (local FM at 100 MHz should be huge).
3. Gain high enough (start 30-40 dB) but not overloading.
4. Bias tee: if using an LNA, is it powered? If not using one, is bias tee wrongly ON into a DC-short antenna?
5. Correct sample format when reading a file (cu8 vs cs8 vs cf32 mismatch = noise or garbage).
6. Direct-sampling/HF: on V3 you need `direct_samp=2`; on V4 you need the blog driver and the
   built-in upconverter path (just tune to the HF frequency).
7. The signal may simply not be present now (satellite not overhead, station off air, wrong ITU region band).

## 8. Distorted / no audio on FM

- Wrong deemphasis (75 us Americas/Korea/Japan vs 50 us elsewhere) -> muffled or shrill.
- Insufficient `fs`/quad rate for WBFM (need >= 200 kHz through the discriminator).
- Squelch set too high (silence) or too low (noise). 
- Audio sample rate not exactly 48000/44100 -> stutter; resample properly.
- Clipping in the demod chain -> add AGC before, normalize after.

## 9. Poor decode rate (ADS-B, ISM, digital)

- Add a **band-pass filter + LNA at the antenna** for the target band; this helps more than gain.
- Improve the antenna (correct length, higher, clear of obstructions) and reduce coax loss.
- Correct ppm for narrowband digital.
- Reduce local noise (ferrites, move antenna, battery power to test).
- Check gain staging: too little misses weak frames, too much overloads on strong ones. Tune for
  the best message rate, not the highest gain.

## 10. USB/host noise, spurs, birdies

- Spurs that move with `fs` (not the antenna) are internal (clock harmonics). Change `fs` slightly,
  or tune so the spur falls outside your signal.
- USB hash: ferrite chokes on USB and power cables, a powered hub with clean supply, shielded/short
  cables, or a USB isolator. Laptop chargers inject noise; test on battery.

## 11. GNU Radio specific

- Type mismatch (red block/port): match cf32 vs f32 vs short; insert converters.
- No Throttle with a hardware source (causes runaway) or two Throttles (causes stutter).
- Audio sink rate must be exactly 48000/44100; use Rational Resampler.
- `firdes.WIN_*` moved to `fft.window.WIN_*` in 3.10 (import error on old flowgraphs).
- Missing OOT block after install: `sudo ldconfig`, check `PYTHONPATH`/`GRC_BLOCKS_PATH`, match the
  module's GNU Radio version.

## 12. When to suspect the hardware itself

Rare, but: no device on any port/OS/cable after driver steps; `hackrf_info` reports "CPLD checksum
mismatch"; RTL-SDR reads only noise on all bands including strong FM with a known-good antenna;
visible physical damage or overheating. Try a second computer to isolate host vs device. Most
"broken SDR" reports are cables, drivers, gain, or antenna.

## 13. Diagnostic commands

```
rtl_test -t                 # tuner + sample-rate sanity
rtl_test -p                 # ppm drift estimate (let it run a minute)
rtl_eeprom                  # serial/config
hackrf_info ; hackrf_debug --si5351c -n 0 -r    # HackRF health
SoapySDRUtil --probe="driver=rtlsdr"            # capabilities, gains, rates
kal -s GSM900 ; kal -c <ch>                      # ppm from GSM
uhd_usrp_probe                                   # USRP details
python scripts/probe_devices.py                  # all of the above, summarized
python scripts/iq_info.py cap.cu8 --fs 2.4e6 --fc 433.92e6   # format/DC/clipping/BW check
```
