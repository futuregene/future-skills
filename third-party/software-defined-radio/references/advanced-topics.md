# Advanced SDR Topics

Pointers and starting math for work beyond basic receive/decode. Each section is a map to the
right tool and the key parameters, not a full tutorial.

## 1. Direction finding (DF) and geolocation

- **Amplitude/rotating-antenna**: turn a Yagi/loop for peak/null; simplest, manual.
- **Phase interferometry (coherent arrays)**: multiple coherent receivers (KrakenSDR = 5 RTL-SDR
  on one clock; USRP/Lime/BladeRF multi-channel). Estimate angle of arrival with **MUSIC** or
  **root-MUSIC**/ESPRIT from the array covariance matrix. Element spacing 0.1-0.5 lambda; a uniform
  circular array (UCA) resolves 360 degrees, a uniform linear array (ULA) has front/back ambiguity.
- **TDOA (time difference of arrival)**: several separated, time-synced receivers cross-correlate
  the same signal; hyperbolic multilateration gives position. Needs accurate time (GPSDO/PPS) and a
  signal with sharp features. Tools: KrakenSDR DoA, `df-aggregator`, RTLSDR-Airband + Kraken, or
  custom cross-correlation.
- Calibration: a shared noise source (Kraken) or an injected reference equalises channel phase.

## 2. Passive radar

- Use a broadcast **illuminator of opportunity** (FM, DAB, DVB-T) as the transmitter. One channel
  is the reference (pointed at the transmitter), another the surveillance (pointed at the target
  area). Cross-ambiguity function (range-Doppler) reveals moving targets after clutter cancellation
  (e.g. adaptive/CLEAN, ECA). Needs coherent multichannel (KrakenSDR, USRP B210). See gr-radar,
  `blah2`, and Malcolm Robb / OpenPR-style projects.

## 3. Coherent and phase-array receive

- Coherence needs a shared **sample clock** and known/calibrated **LO phase**. Devices: USRP B210
  (two RX on one AD9361), RSPduo, Lime/Blade 2x2, KrakenSDR, or multiple USRPs with 10 MHz + PPS and
  `set_time_next_pps`/`set_time_unknown_pps` then a phase-cal with a splitter.
- Beamforming: weight and sum channels to steer a beam or null an interferer (MVDR/Capon, LCMV).
- Applications: DF, passive radar, MIMO experiments, gain in a direction.

## 4. GNSS: reception, timing, and simulation

- **Reception**: GNSS-SDR takes IQ at >= 2 MS/s around 1575.42 MHz (L1) from an active antenna
  (bias tee) and produces a position/time fix. Acquisition searches code phase x Doppler; tracking
  runs DLL (code) + PLL/FLL (carrier). Good SDR sanity and timing test.
- **Timing/1PPS**: a GPSDO disciplines your SDR reference to GPS for ppm-accurate, coherent work.
- **Simulation (`gps-sdr-sim`, `gnss-sdr-sim`)**: generates IQ for a chosen location/time to feed a
  TX. **Only in a fully shielded/cabled setup**: GNSS spoofing over the air is illegal and dangerous
  (aviation, timing infrastructure). Attenuate heavily and contain all RF.

## 5. Machine learning for RF (RFML)

- **Modulation classification**: CNN/ResNet on IQ (RadioML 2016/2018 datasets, DeepSig); input is
  Nx2 (I,Q) or spectrogram images; achieves high accuracy above ~0 dB SNR. Frameworks: PyTorch/TF,
  `torchsig` (Torchsig library + datasets), GNU Radio + `gr-inspector` for classical features.
- **Signal detection/segmentation**: object detection (YOLO-style) on spectrograms to find and box
  bursts; useful for wideband survey.
- **RF fingerprinting**: identify a specific transmitter from hardware imperfections (I/Q offset,
  phase noise, transient) with a classifier; used for auth and for spoofing detection.
- **Anomaly detection**: autoencoders on spectrograms flag unexpected emissions.
- Pitfalls: models overfit to the capture hardware and channel; augment with realistic impairments
  (CFO, multipath, AGC), test cross-device, and beware dataset leakage.

## 6. FPGA and high-throughput (RFNoC, gateware)

- **RFNoC** (USRP): build DSP blocks in the FPGA (Verilog/HLS) to offload filtering/FFT/decimation at
  full ADC rate; connect to GNU Radio via RFNoC blocks. For rates the host cannot sustain.
- **LimeSDR/BladeRF gateware**: custom FPGA logic for on-device processing (e.g. pre-filtering,
  packet detection) to cut USB load.
- Consider FPGA only when host DSP cannot keep up (very high `fs`, real-time closed loops, latency).

## 7. Wideband survey and spectrum monitoring

- **Sweeping**: `hackrf_sweep -f 1:6000` (1 MHz-6 GHz), `rtl_power -f 24M:1766M:1M` (slow, tuner
  steps), `soapy_power`, SDRangel. Feed to a heatmap (`heatmap.py`, QSpectrumAnalyzer, `rtl_power`
  + gnuplot) for a spectrogram over time.
- **Occupancy studies**: log power per channel over hours/days; watch duty cycle and diurnal patterns.
- Trade-off: a single SDR sweeps sequentially (misses bursts between visits); coherent wideband
  (USRP 200 MS/s, multiple SDRs) captures continuously.

## 8. Encryption, scrambling, and FEC in signals (analysis, not defeat)

- Many digital protocols apply **scrambling/whitening** (LFSR, additive) to balance bits; you must
  descramble to see structure. The polynomial is usually in the standard/datasheet (e.g. CC1101,
  802.15.4, DVB).
- **FEC**: convolutional (Viterbi), Reed-Solomon, LDPC, turbo, polar. GNU Radio `gr-fec` and
  `libfec` decode standard configurations; satellites often use conv+RS (CCSDS) which gr-satellites
  handles.
- **Interleaving/deinterleaving** must be undone before FEC. Order (RX): sync -> descramble ->
  deinterleave -> FEC decode -> CRC.
- **Encryption**: analysing framing and unencrypted headers is normal; decrypting protected
  communications (cellular, encrypted PS) is out of scope and illegal. Working with your own keys on
  your own devices (e.g. your LoRaWAN app keys) is fine.

## 9. Full-stack lab systems (your own network, shielded)

- **GSM/LTE/5G lab**: srsRAN (LTE/5G) or Osmocom (2G/3G) with a full-duplex SDR (USRP B210/Lime),
  your own test SIMs (sysmoUSIM), inside a shielded enclosure and, where required, under a test
  licence. For teaching/research on protocol internals; never on a public band with real subscribers.
- **LoRaWAN**: run your own gateway + network server (ChirpStack) and nodes; decode with your keys.
- **DVB/ATSC**: transmit a test multiplex into a cabled receiver.

## 10. Timing, synchronization, and SDR clusters

- **Reference**: 10 MHz + 1PPS from a GPSDO to every SDR for frequency and time alignment.
- **Distributed capture (SatNOGS-style)**: many stations, scheduled by TLE, uploading observations;
  good for satellites and for TDOA networks.
- **Streaming fabrics**: ZeroMQ/UDP/VITA-49 to move IQ between machines; watch bandwidth (20 MS/s
  cf32 = 160 MB/s) and use compression or on-node decimation.

## 11. Where to go deeper

- Books: *Software-Defined Radio for Engineers* (Collins/Wyglinski, free PDF from Analog Devices),
  Richard Lyons *Understanding DSP*, *Understanding LTE with MATLAB*, GNU Radio tutorials.
- Sites: pysdr.org (Marc Lichtman, excellent free IQ/DSP course), sigidwiki.com (signal ID),
  rtl-sdr.com (news/how-tos), the GNU Radio wiki, the SatDump/gr-satellites docs.
- Datasets: DeepSig RadioML, Torchsig; SigMF example captures.
- Communities: r/RTLSDR, r/amateurradio, GNU Radio Discourse/Matrix, local amateur clubs (for
  licensing and antennas).
