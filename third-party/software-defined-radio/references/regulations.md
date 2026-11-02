# Spectrum Regulations for SDR Users

This is orientation, not legal advice. Rules change; verify against your national regulator
before transmitting or before decoding anything sensitive. Two principles hold almost everywhere:

1. **Receiving is lightly regulated; transmitting is heavily regulated.** You may listen to most
   of the spectrum, but you generally may not divulge, use, or record certain contents (see below),
   and you may not transmit without a licence or an unlicensed-band exemption.
2. **Some contents are protected even from listening**: cellular/mobile telephony, other people's
   private/two-way communications, and encrypted public-safety traffic. Decrypting protected
   communications is illegal in most jurisdictions regardless of the tool.

## 1. ITU framework

- The ITU Radio Regulations divide the world into three Regions: **1** (Europe, Africa, Middle
  East, former USSR, Mongolia), **2** (Americas), **3** (Asia-Pacific, including Indonesia,
  Australia, most of South/East Asia). Frequency allocations differ by region; a band that is ISM
  or amateur in one region may be licensed in another.
- National regulators implement the ITU table with their own band plan and licensing.

## 2. By jurisdiction (receive vs transmit, key points)

### United States (FCC)
- **Receive**: legal for most bands. **Illegal to intercept or divulge** cellular/PCS calls
  (Communications Act 47 USC 605; ECPA 18 USC 2510+). Scanners sold in the US are cellular-blocked.
- **Transmit**: needs a licence (amateur Technician/General/Extra, GMRS, etc.) or must be under
  Part 15 (unlicensed) or Part 97 (amateur) rules. Part 15 devices (Wi-Fi, 433/915 ISM) have EIRP
  limits; a HackRF/Pluto is not a certified Part 15 device, so arbitrary TX on ISM bands is not
  automatically legal.
- Amateur: exams via VEC; call sign required; band plan by license class.

### United Kingdom (Ofcom)
- **Receive**: you may listen only to transmissions you are authorized to (broadcast, amateur,
  Citizens' Band, your own licensed radios) under the Wireless Telegraphy Act 2006; listening to
  other services (e.g. police, aircraft, private) is technically an offence, and it is an offence
  to disclose what you hear. Enforcement in practice focuses on disclosure/misuse.
- **Transmit**: Amateur licence (Foundation/Intermediate/Full) or a licence-exempt band (PMR446,
  LPD433 within limits, Wi-Fi). Ofcom publishes IR 2030 for licence-exempt SRDs.

### European Union / CEPT (ETSI harmonised SRDs)
- SRD bands (ERC/REC 70-03, ETSI EN 300 220): 433.05-434.79 MHz (10 mW ERP typical), 863-870 MHz
  (SRD, incl. LoRa 868, duty-cycle limited), 2.4 and 5 GHz (Wi-Fi/RLAN). Amateur via national
  CEPT-harmonised licences. Reception rules vary by country (some allow broad listening, some restrict).

### Indonesia (Komdigi / Ditjen SDPPI) — ITU Region 3
Regulator: **Kementerian Komunikasi dan Digital (Komdigi)**, spectrum arm **Direktorat Jenderal
Sumber Daya dan Perangkat Pos dan Informatika (Ditjen SDPPI)**. Legal base: **UU 36/1999 tentang
Telekomunikasi**, updated by **UU 6/2023 (Cipta Kerja)**, and **PP 5/2021 / PP 46/2021**;
enforcement of illegal transmission and interference sits under these.

License types:
- **Izin Pita Frekuensi Radio (IPFR)** — spectrum band licence (operators, e.g. cellular).
- **Izin Stasiun Radio (ISR)** — per-station/channel licence (broadcast, point-to-point, etc.).
- **Izin Kelas (class licence)** — attaches to certified devices; no individual permit needed if
  the device meets the technical standard. This covers Wi-Fi/RLAN, Bluetooth, LPWAN/LoRa, SRD,
  and low-power devices. Current class-licence rules: **Permen Kominfo 2/2023** as amended by
  **Permen Komdigi 2/2025**; SRD technical details also in **Kepmen/Keputusan Menteri Komdigi
  260/2024**. Verify the latest numbers on the SDPPI site before relying on them.

Unlicensed / class-licence bands commonly used (confirm current limits with SDPPI):
- **433.05-434.79 MHz** SRD (low power; remote controls, sensors).
- **920-923 MHz** — the LPWAN/LoRa/IoT band in Indonesia (note: **not** 915 MHz like the US, and
  narrower than the EU 863-870; set LoRa gateways/nodes to the 920-923 plan, AS923).
- **2400-2483.5 MHz** — Wi-Fi/Bluetooth/Zigbee (RLAN, EIRP limited).
- **5150-5250, 5250-5350, 5470-5725, 5725-5825 MHz** — RLAN (indoor/outdoor and power limits per band).
- 24 GHz, 57-66 GHz, 76-81 GHz (radar) and others per the SRD decree.

Devices: anything transmitting and marketed in Indonesia needs **SDPPI type approval
(sertifikasi perangkat)**. A HackRF/Pluto/USRP is a lab instrument, not a certified device, so
transmitting on air with one is only lawful under an appropriate licence or in a way that emits no
usable RF off-premises (cabled/shielded lab).

Amateur radio: organised under **ORARI** (Organisasi Amatir Radio Indonesia, IARU member);
operators hold an **IAR (Izin Amatir Radio)** and a callsign after examination; band plan follows
IARU Region 3. There is a separate citizens' service (**KRAP/RAPI**, "Izin Komunikasi Radio
Antar Penduduk").

Receiving: listening to broadcast, amateur, aviation, maritime, and unencrypted telemetry is
normal. Intercepting private communications and cellular content is prohibited; **penyadapan**
(unlawful interception) is a criminal offence under the Telecommunications Law and the ITE Law
(UU 11/2008 as amended by UU 1/2024). Do not decode, log, or disclose private communications.

### Australia (ACMA), Canada (ISED), and others
- Similar structure: amateur licence for HF/VHF/UHF TX; class licences / LIPD for SRDs; receive
  broadly allowed but disclosure of intercepted private comms restricted. Check the national LIPD
  / RSS / band plan.

## 3. What is generally safe to receive anywhere

Broadcast (AM/FM/DAB/DVB), amateur bands, aviation (ADS-B, ACARS, VOR/ILS, airband voice),
maritime (AIS, marine VHF, NAVTEX), weather satellites (APT/LRPT/HRIT) and other satellite
downlinks that are open broadcasts, GNSS, time signals, ISM/SRD telemetry (rtl_433 sensors, your
own LoRa), and radiosondes. These are unencrypted broadcasts or telemetry not directed at a
specific private party.

## 4. What to avoid (receive)

- **Cellular voice/data** (GSM/LTE/5G subscriber traffic) — protected and encrypted; analyzing only
  the unencrypted broadcast system-information for research is the boundary many researchers observe,
  but capturing/decrypting subscriber content is illegal.
- **Encrypted public-safety** (police/fire/EMS on encrypted DMR/P25/TETRA) — do not attempt to decrypt.
- **Private/business two-way** where local law forbids listening (UK) or disclosure (most places).
- **Pager content** — often personal/medical; many jurisdictions forbid decoding/disclosure.
- **Anything you would then divulge or act on** — even where listening is legal, using or sharing
  the contents usually is not.

## 5. Transmitting — the checklist

Only transmit if at least one is true, and then within its limits:
1. You hold the relevant **amateur licence** and stay within your class's band plan, power, and mode.
2. You are within an **unlicensed/class-licence band** using a **certified device** at legal EIRP
   and duty cycle (a bare SDR is usually not certified).
3. You are in a **shielded/cabled lab** so no usable RF is emitted off-premises, and you are not on
   a band where even leakage is dangerous (GNSS, aviation, cellular uplink, emergency).

Never transmit on: aviation (108-137), GNSS (1.2/1.5/1.6 GHz), emergency/distress (121.5, 243,
406 MHz beacons, 156.8 marine ch16), cellular uplink bands, or any safety-of-life service.
Jamming and intentional interference are criminal offences everywhere. See
`transmission-lab-safety.md` for the physical setup.

## 6. How to verify current rules

- Find your **national regulator's band plan / allocation table** (FCC OET, Ofcom IR2030, SDPPI/
  Komdigi spectrum pages, ACMA, ISED RSS) and the **SRD / class-licence document**.
- For amateur specifics, use your **national amateur society** band plan (ARRL, RSGB, ORARI, WIA).
- For a signal you found, sigidwiki plus the allocation chart usually identify the service and its status.
- When advising a user, state the country if known and cite the instrument by name/number as
  above, and tell them to confirm the current version, because these are revised often.
