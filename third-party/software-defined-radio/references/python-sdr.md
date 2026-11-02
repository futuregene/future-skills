# Python for SDR

numpy/scipy DSP, reading every IQ format, live streaming with each driver, and SigMF.
All examples assume `import numpy as np` and complex baseband.

## 1. Reading and writing IQ files

```python
import numpy as np

def read_iq(path, fmt=None, count=-1, offset=0):
    """Return complex64 IQ. fmt in {cu8,cs8,cs16,cs12,cf32,cf64}; inferred from ext if None."""
    if fmt is None:
        fmt = path.split(".")[-1].lower()
    dt = {"cu8":np.uint8,"cs8":np.int8,"cs16":np.int16,"cf32":np.float32,"cf64":np.float64}[fmt]
    n = count if count < 0 else count*2
    raw = np.fromfile(path, dtype=dt, count=n, offset=offset*np.dtype(dt).itemsize*2).astype(np.float32)
    if fmt == "cu8":  raw = (raw - 127.5) / 127.5
    elif fmt == "cs8": raw = raw / 127.5
    elif fmt == "cs16": raw = raw / 32767.0
    elif fmt == "cf64": raw = raw.astype(np.float32)
    return raw[0::2] + 1j*raw[1::2]

def write_iq(path, iq, fmt="cf32"):
    inter = np.empty(iq.size*2, dtype=np.float32)
    inter[0::2], inter[1::2] = iq.real, iq.imag
    if fmt == "cf32":  inter.tofile(path)
    elif fmt == "cu8": (inter*127.5 + 127.5).clip(0,255).astype(np.uint8).tofile(path)
    elif fmt == "cs8": (inter*127.5).clip(-128,127).astype(np.int8).tofile(path)
    elif fmt == "cs16":(inter*32767).clip(-32768,32767).astype(np.int16).tofile(path)
```

- **cu8** (rtl_sdr): unsigned 8-bit, bias 127.5. **cs8** (hackrf): signed 8-bit.
  **cs16** (UHD sc16, SDRplay, Pluto): signed 16-bit; Pluto/AD936x is 12-bit data in the low
  bits, so divide by 2048 not 32768 if you want physical scaling (either works for DSP).
- Interleaving is always I then Q, little-endian, no header (except WAV/SigMF).
- WAV IQ (SDR#/SDR++): 2-channel PCM (ch0=I, ch1=Q); read with `scipy.io.wavfile` or `soundfile`;
  the sample rate field holds `fs`; center frequency is in an `auxi`/`riff` chunk (SDR#) or a
  companion metadata file.

## 2. Basic DSP recipes

```python
from scipy import signal

# frequency shift
def shift(iq, f_off, fs):
    n = np.arange(iq.size)
    return iq * np.exp(-2j*np.pi*f_off/fs*n)

# decimate with anti-alias (chain for large factors)
def decim(iq, factor):
    while factor > 1:
        f = min(factor, 8); iq = signal.decimate(iq, f, ftype="fir", zero_phase=False); factor //= f
    return iq

# PSD (one-sided=False keeps negative freqs)
def psd(iq, fs, nfft=4096):
    f, p = signal.welch(iq, fs, nperseg=nfft, return_onesided=False, detrend=False)
    return np.fft.fftshift(f), np.fft.fftshift(10*np.log10(p+1e-20))

# spectrogram / waterfall
f, t, Sxx = signal.spectrogram(iq, fs, nperseg=1024, noverlap=768, return_onesided=False)
Sxx = np.fft.fftshift(10*np.log10(Sxx+1e-20), axes=0)

# FM discriminator
def fm_demod(iq):  return np.angle(iq[1:]*np.conj(iq[:-1]))

# AM envelope
def am_demod(iq):  x = np.abs(iq); return x - x.mean()

# SSB (USB): shift suppressed carrier to 0, low-pass, take real
def ssb_usb(iq, fs, bw=3000):
    b = signal.firwin(301, bw/(fs/2))
    return np.real(signal.lfilter(b, 1, iq))
```

## 3. Carrier and timing recovery (minimal)

```python
# Coarse frequency for BPSK via x^2 line
def coarse_freq_bpsk(iq, fs):
    sq = iq**2
    F = np.fft.fftshift(np.abs(np.fft.fft(sq)))
    fr = np.fft.fftshift(np.fft.fftfreq(iq.size, 1/fs))
    return fr[np.argmax(F)]/2

# Costas loop (BPSK order 2)
def costas_bpsk(iq, bw=2*np.pi/200):
    phase=freq=0.0; a1=bw; a2=bw*bw/4; out=np.empty_like(iq)
    for i,s in enumerate(iq):
        y = s*np.exp(-1j*phase); out[i]=y
        err = np.real(y)*np.imag(y)         # BPSK error
        freq += a2*err; phase += freq + a1*err
    return out

# Gardner timing (2 samples/symbol in, 1 out)
def gardner(x, sps=2, bw=0.01):
    mu=0.0; out=[]; i=sps
    while i < len(x)-sps:
        s=x[int(i)]; prev=x[int(i-sps)]; mid=x[int(i-sps//2)]
        err = np.real(np.conj(mid)*(s-prev))
        mu += sps + bw*err; out.append(s); i += mu; mu=0
    return np.array(out)
```
For real work use GNU Radio `Symbol Sync`/`Costas Loop` or `commpy`; the above is for learning.

## 4. Live streaming

### pyrtlsdr (RTL-SDR only, simplest)

```python
from rtlsdr import RtlSdr
sdr = RtlSdr()
sdr.sample_rate = 2.4e6; sdr.center_freq = 100.1e6; sdr.gain = 30      # or 'auto'
sdr.set_bias_tee(False)                                                # V3/V4
iq = sdr.read_samples(256*1024)          # returns complex128 already scaled
# async: sdr.read_samples_async(callback, num_samples)
sdr.close()
```

### SoapySDR (any device, portable)

```python
import SoapySDR, numpy as np
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
sdr = SoapySDR.Device(dict(driver="rtlsdr"))          # or hackrf, airspy, sdrplay, plutosdr, uhd, lime, bladerf
sdr.setSampleRate(SOAPY_SDR_RX, 0, 2.4e6)
sdr.setFrequency(SOAPY_SDR_RX, 0, 100.1e6)
sdr.setGain(SOAPY_SDR_RX, 0, 30)                       # or per-stage setGain(..., "LNA", x)
st = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
sdr.activateStream(st)
buf = np.empty(16384, np.complex64)
for _ in range(100):
    sr = sdr.readStream(st, [buf], len(buf))           # sr.ret = samples read, check sr.ret>0
    # process buf[:sr.ret]
sdr.deactivateStream(st); sdr.closeStream(st)
```

### pyadi-iio (Pluto)

```python
import adi
sdr = adi.Pluto("ip:192.168.2.1")            # or "usb:"
sdr.sample_rate = int(2.5e6)
sdr.rx_lo = int(100_100_000)
sdr.rx_rf_bandwidth = int(2e6)
sdr.gain_control_mode_chan0 = "manual"; sdr.rx_hardwaregain_chan0 = 40
sdr.rx_buffer_size = 32768
iq = sdr.rx()                                # complex ndarray, scaled to +-2048
# TX (lab only): sdr.tx_lo=...; sdr.tx_hardwaregain_chan0=-20; sdr.tx_cyclic_buffer=True; sdr.tx(samples)
```

### UHD (USRP)

```python
import uhd, numpy as np
usrp = uhd.usrp.MultiUSRP("")                # or "type=b200"
usrp.set_rx_rate(2e6); usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(100.1e6)); usrp.set_rx_gain(40)
samps = usrp.recv_num_samps(1_000_000, 100.1e6, 2e6, [0], 40)   # convenience one-shot
```

## 5. SigMF

```python
# pip install sigmf
from sigmf import SigMFFile, sigmffile
import datetime as dt, numpy as np

iq = read_iq("cap.cs16","cs16")
iq.astype(np.complex64).tofile("cap.sigmf-data")   # store as cf32
meta = SigMFFile(
    data_file="cap.sigmf-data",
    global_info={
        SigMFFile.DATATYPE_KEY: "cf32_le",
        SigMFFile.SAMPLE_RATE_KEY: 2.4e6,
        SigMFFile.HW_KEY: "RTL-SDR Blog V4",
        SigMFFile.AUTHOR_KEY: "you",
        SigMFFile.DESCRIPTION_KEY: "433.92 MHz ISM capture",
        SigMFFile.VERSION_KEY: "1.2.0",
    })
meta.add_capture(0, metadata={SigMFFile.FREQUENCY_KEY: 433.92e6,
                              SigMFFile.DATETIME_KEY: dt.datetime.utcnow().isoformat()+"Z"})
meta.add_annotation(0, 4096, metadata={SigMFFile.FLO_KEY: 433.90e6, SigMFFile.FHI_KEY: 433.94e6,
                                       SigMFFile.LABEL_KEY: "OOK burst"})
meta.tofile("cap.sigmf-meta")

# read back
sf = sigmffile.fromfile("cap.sigmf-meta")
data = sf.read_samples()                    # complex64
fs = sf.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
```

Datatype strings: `cf32_le`, `ci16_le`, `ci8`, `cu8` (as `cu8` non-standard; SigMF uses
`cu8`? use `ci8`/` cf32_le`). A `.sigmf-data` + `.sigmf-meta` pair (optionally zipped as
`.sigmf`) is the portable, self-documenting capture format; share these, not bare `.cu8`.

## 6. Plotting

```python
import matplotlib.pyplot as plt
f, p = psd(iq, fs); plt.plot((f+fc)/1e6, p); plt.xlabel("MHz"); plt.ylabel("dB"); plt.show()
plt.specgram(iq, NFFT=1024, Fs=fs, noverlap=768); plt.show()
plt.plot(np.real(sym), np.imag(sym), '.'); plt.axis('equal'); plt.title("constellation")   # after timing recovery
```
For live/fast plots use `pyqtgraph` (10-100x faster than matplotlib) or GNU Radio QT sinks.

## 7. Performance

- Use `np.complex64` everywhere; avoid Python loops in the hot path (vectorize, or use `numba`
  `@njit` for sample-by-sample loops like PLLs).
- FFTs: `scipy.fft` (pocketfft) or `pyfftw` for repeated same-size transforms.
- Stream in blocks; keep filter state with `signal.lfilter(..., zi=zi)` returning updated `zi`.
- Memory: 30 s at 2.4 MS/s cf32 = ~576 MB in RAM; process in chunks (`np.fromfile(..., count=)`
  with `offset=` to page through a big file).
- `scipy.signal.decimate` uses an IIR by default (`ftype='iir'`, phase distortion); pass
  `ftype='fir'` for linear phase, `zero_phase=True` for offline files.

## 8. Common Python gotchas

- Forgetting the 127.5 bias on cu8 leaves a huge DC term and halves your usable range.
- `np.angle` unwrap: FM audio is fine sample-to-sample (`x[1:]*conj(x[:-1])`), but don't
  `np.unwrap` the whole phase for FM (it accumulates).
- `fftfreq`/`fftshift`: after `fftshift`, index 0 is the most negative frequency; label axes carefully.
- SoapySDR `readStream` can return fewer samples than asked or a timeout (`ret == SOAPY_SDR_TIMEOUT`,
  a negative number); always check `sr.ret`.
- Pluto `rx_buffer_size` too small starves throughput; too large adds latency. 2^15-2^18 typical.
- Real vs complex sample counts: a file of N bytes in cu8 holds N/2 complex samples.
