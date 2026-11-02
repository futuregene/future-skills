# IQ Sample Formats and SigMF

Nothing inside a raw IQ file tells you its format, sample rate, or center frequency. You must
record that metadata yourself or you lose the capture. This file lists every common format and
how to store metadata.

## 1. Raw interleaved formats

All are interleaved `I0 Q0 I1 Q1 ...`, little-endian, no header.

| Name | dtype | Bytes/complex sample | Full scale | Written by |
|---|---|---|---|---|
| cu8 (uint8) | unsigned 8-bit | 2 | 0..255, bias 127.5 | `rtl_sdr`, `rtl_tcp`, RTL-SDR tools |
| cs8 (int8) | signed 8-bit | 2 | -128..127 | `hackrf_transfer`, some Airspy |
| cs12 | signed 12-bit packed | 3 | -2048..2047 | some devices raw (rare on disk) |
| cs16 / sc16 (int16) | signed 16-bit | 4 | -32768..32767 (or 12-bit in low bits) | UHD `sc16`, SDRplay, Pluto (`iio`), Airspy `-t 4`? |
| cf32 (float32) | 32-bit float | 8 | ~ -1.0..1.0 | GNU Radio File Sink, most Python, SigMF `cf32_le` |
| cf64 (float64) | 64-bit float | 16 | -1..1 | rare; numpy default if you forget to cast |

Conversions (scale so `|x| ~ 1`):
- cu8 -> float: `(b - 127.5)/127.5`
- cs8 -> float: `b/127.5`
- cs16 (full 16-bit) -> float: `s/32767`; (12-bit justified, e.g. Pluto) `s/2048`
- The DSP is identical regardless of scaling; scaling only matters for absolute level and for
  writing back to an integer format without clipping.

**Sample count from file size**: `n_complex = filesize_bytes / bytes_per_complex_sample`.
A 100 MB cu8 file = 50 M complex samples = 20.8 s at 2.4 MS/s.

## 2. WAV IQ (SDR#, SDR++, HDSDR, SDR Console)

- 2-channel PCM WAV: channel 0 = I, channel 1 = Q; bit depth 8/16/32; the WAV header's sample
  rate field = `fs`.
- **Center frequency** is stored in an extension chunk that differs by program:
  - SDR#: an `auxi` chunk with start/stop time and center frequency.
  - SDR Console / HDSDR: filename convention `HDSDR_YYYYMMDD_HHMMSSZ_<fc>kHz_RF.wav`.
- Read with `scipy.io.wavfile.read` (gives `fs` and an Nx2 array -> `I + 1j*Q`) or `soundfile`.
  You may need to parse the vendor chunk for `fc`; otherwise it is in the filename.
- 4 GB WAV limit (32-bit size field); long high-rate captures overflow it. Use `rf64`/`w64`
  or raw + SigMF for long/fast captures.

## 3. SigMF (the portable, self-describing format)

A capture is two files with the same basename:
- `name.sigmf-data`: raw interleaved samples (any datatype).
- `name.sigmf-meta`: JSON with `global`, `captures[]`, `annotations[]`.
- Optionally zipped together as `name.sigmf` (a plain zip, or a `.sigmf-collection` for sets).

Minimal meta:
```json
{
  "global": {
    "core:datatype": "cf32_le",
    "core:sample_rate": 2400000,
    "core:version": "1.2.0",
    "core:hw": "RTL-SDR Blog V4",
    "core:author": "you",
    "core:description": "433.92 MHz ISM capture"
  },
  "captures": [
    { "core:sample_start": 0, "core:frequency": 433920000,
      "core:datetime": "2026-09-16T04:00:00Z" }
  ],
  "annotations": [
    { "core:sample_start": 4096, "core:sample_count": 2048,
      "core:freq_lower_edge": 433900000, "core:freq_upper_edge": 433940000,
      "core:label": "OOK burst" }
  ]
}
```
Datatype strings: `cf32_le`, `cf64_le`, `ci16_le`, `ci8`, `cu8`, `cf32_be` etc.
(`c` = complex, `f/i/u` = float/signed/unsigned, bits, endianness). Use `cf32_le` when in doubt.

Tools: `pip install sigmf`; `scripts/sigmf_write.py` writes a meta file for an existing capture;
inspectrum, URH, SatDump, and IQEngine read SigMF directly. Share SigMF, not bare `.cu8`.

## 4. Other containers

- **GNU Radio metadata files** (`File Meta Sink`): a header-per-segment format with `rx_time`,
  `rx_rate`, `rx_freq` tags; read with `gnuradio.blocks.parse_file_metadata`.
- **npy/npz** (numpy): convenient in Python, not interoperable with SDR tools.
- **HDF5**: used by some research pipelines; store `fs`, `fc` as attributes.
- **VITA-49 (VRT)**: the professional streaming standard (USRP/X-series over the wire); carries
  timestamps and context packets; not a common on-disk hobby format.

## 5. Naming convention (when you must use raw)

`YYYYMMDD_HHMMSSZ_<fc_Hz>_<fs_Hz>_<fmt>[_gain][_note].<ext>`

Example: `20260916_040000Z_433920000_2400000_cu8_g30_doorbell.cu8`.
This encodes the four things you cannot recover from the bytes: center, rate, format, and context.

## 6. Converting between formats

```bash
# with the bundled tool (also shift / decimate / trim)
python scripts/iq_convert.py in.cu8 out.cf32 --fs 2.4e6
python scripts/iq_convert.py in.cu8 out.cf32 --fs 2.4e6 --shift -250e3 --decim 10 --start 1.0 --dur 5.0

# with SoX-like manual numpy (see python-sdr.md read_iq/write_iq)
# with GNU Radio: File Source (cu8 -> use 'Char to Float' x2 + scale, or IShort) -> File Sink cf32
```

Rules when converting:
- Match the scaling (subtract 127.5 for cu8, divide correctly) or levels/clipping change.
- Down-converting to a smaller integer type (cf32 -> cu8/cs8) throws away dynamic range; only do
  it to feed a tool that requires it (rtl_433 wants cu8/cs16; URH auto-detects; inspectrum reads all).
- Preserve or regenerate metadata; a converted file with no meta is as lost as the original.

## 7. Which format does each tool want?

| Tool | Reads | Writes |
|---|---|---|
| rtl_sdr | - | cu8 |
| hackrf_transfer | cs8 | cs8 |
| GNU Radio File Source/Sink | cf32 (and others via type) | cf32 |
| inspectrum | cu8/cs8/cs16/cf32/f32/cf64, SigMF | - |
| URH | auto-detects cu8/cs8/cs16/cf32/wav/sigmf/complex | same set |
| rtl_433 -r | cu8, cs16, cf32 (with `-s`) | - |
| SatDump baseband | cu8/cs8/cs16/cf32/wav, SigMF | cf32/etc |
| SDR++ recorder | - | WAV (with metadata) or raw |
| IQEngine / SigMF ecosystem | SigMF | SigMF |
