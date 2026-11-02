# Transmission and Lab Safety

Transmitting is only lawful under a licence, within an unlicensed/class-licence band with a
certified device, or in a setup that emits no usable RF off-premises. This file covers the
physical and procedural side once you have established that you are allowed to transmit. See
`regulations.md` for whether you are allowed at all.

## 1. Before keying up: the checklist

1. **Authorization confirmed** (licence and band plan, or unlicensed-band limits, or cabled lab).
2. **Right band, right mode, legal power and duty cycle** for that authorization.
3. **Antenna or dummy load connected** and matched (SWR < 2:1). Never transmit into an open/short
   or a disconnected port; the PA can be damaged and you radiate reflections.
4. **Harmonic filter** in line for the band (a low-pass or band-pass), because SDR PAs (HackRF,
   Pluto) put out strong harmonics that land in other services.
5. **Start at minimum gain/power**, verify on a second receiver, then raise only as needed.
6. **Never transmit** on aviation, GNSS, emergency/distress, cellular uplink, or any safety-of-life
   frequency, even briefly, even "to test".
7. **RF exposure**: keep people out of the near field; higher power and higher bands need more distance.

## 2. Cabled / shielded lab setup (the default for experiments)

For replaying or emulating your own devices without radiating:

```
SDR TX out --[SMA coax]--[30-40 dB attenuator]--[optional band-pass filter]--> target RX (SMA)
```
or put both the SDR and the device under test inside a **shielded box / RF enclosure** (a
faraday bag or a proper screened box), or a small **anechoic/absorber-lined enclosure**.

- **Attenuation**: SDR TX outputs can be 0 to +15 dBm; a receiver front end wants far less. Use
  30-40 dB of fixed attenuation (or a step attenuator) so you (a) protect the receiver and (b)
  keep leakage low. Two 20 dB attenuators in series avoid a single point of failure.
- **Never connect a transmitter directly to an SDR receiver input** without heavy attenuation; +10
  dBm into an RTL-SDR/HackRF RX destroys the front end (max ~-10 dBm, absolute max often lower).
- **Leakage still happens** through cases and cables; a cabled setup is "low emission", not zero.
  For anything that could interfere (GNSS spoofing tests, cellular), use a properly shielded room.

## 3. Device TX quick reference

| Device | TX range | Max output | Gain control | CLI |
|---|---|---|---|---|
| HackRF One | 1 MHz-6 GHz (half-duplex) | ~ +10 to +15 dBm low bands, less >2 GHz | TX VGA 0-47 dB (`-x`), amp +14 dB (`-a 1`) | `hackrf_transfer -t f.cs8 -f <Hz> -s <sps> -x 20` |
| ADALM-Pluto | 325-3800 MHz (70-6000 hacked), full-duplex | ~ +7 dBm at 0 attenuation | attenuation 0 to -89.75 dB (`tx_hardwaregain` negative) | pyadi-iio `sdr.tx(samples)`; `iio_attr` |
| LimeSDR / Mini | 10 MHz-3.5/3.8 GHz, full-duplex | ~0 to +10 dBm band-dependent | per-stage gain | LimeSuite / SoapySDR / `gr-limesdr` |
| BladeRF 2.0 | 47 MHz-6 GHz, full-duplex | up to ~ +8 dBm | -24 to +66 dB | `bladeRF-cli -e "set gain tx1 30"` |
| USRP B2x0 | 70 MHz-6 GHz, full-duplex | ~ +10 dBm | 0-89.8 dB | UHD `tx_samples_from_file`, `set_tx_gain` |

RTL-SDR, Airspy, SDRplay are **receive-only**; they cannot transmit.

## 4. Building a TX signal (GNU Radio / Python)

- Keep the sample magnitude below full scale (|x| <= 0.7) to avoid DAC clipping and splatter.
- Use proper pulse shaping (RRC for PSK, Gaussian for GFSK) to keep the spectrum inside the channel.
- Match the device minimum sample rate (HackRF >= 2 MS/s): interpolate your baseband up to the
  device rate.
- For bursts, use tagged-stream/PDU bursts with start/end-of-burst tags (UHD `tx_sob`/`tx_eob`) or
  cyclic buffers (Pluto `tx_cyclic_buffer`) and mute between bursts.
- Verify your generated signal by looping back into a receiver (through attenuation) before doing
  anything over the air.

## 5. Replay experiments (only on devices you own)

Legitimate: characterising the security of **your own** remote/sensor/alarm in a cabled lab.
Method: record the device's transmission (`iq_info.py` to confirm centre/BW), then replay the same
IQ through the TX device into the receiver of your own equipment via coax + attenuator. Report
whether the design is replay-vulnerable and recommend mitigations (rolling codes, challenge-
response, timestamps, encryption).

Out of scope / do not do: replaying or spoofing against systems you do not own (vehicles, garages,
gates, alarms, meters, aircraft, GNSS, cellular), defeating rolling-code or crypto to gain access,
or any transmission intended to interfere with or deny a service. This skill will not help with
those; they are illegal (unauthorized access, interference, and often theft/fraud) regardless of
"research" framing.

## 6. Hardware safety

- **Static**: SDR RF inputs are ESD-sensitive; ground yourself, use ESD protection on outdoor antennas.
- **DC on the line**: bias tees put 4.5-12 V on the coax. Only enable with an LNA/antenna that
  expects it; a DC-shorted antenna + bias tee can damage the SDR.
- **Overload**: strong signals (nearby transmitters, your own TX leakage) can exceed the RX max
  input (~-10 dBm). Add attenuation/filtering; never share an antenna between a transmitter and an
  unprotected SDR RX.
- **Heat**: LimeSDR/BladeRF/USRP run hot under load; provide airflow/heatsinks. HackRF gets warm on
  long TX.
- **Power**: high sample rates + LNA + SBC need a solid supply; undervoltage corrupts samples.
- **Antenna placement**: keep clear of power lines; ground masts; use lightning arrestors;
  disconnect in storms.
- **RF exposure**: for any real over-the-air TX, respect the regulator's maximum permissible
  exposure limits; do not stand in front of a transmitting directional antenna.

## 7. Interference: recognise and avoid causing it

- Harmonics and wideband noise from cheap PAs are the usual culprits; always filter.
- If a device or neighbour reports interference, stop transmitting and investigate; intentional
  interference is a criminal offence.
- Test into a load or shielded setup first; go on air at minimum power; monitor adjacent channels.
