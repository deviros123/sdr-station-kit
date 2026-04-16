#!/usr/bin/env python3
"""Record radiofax audio from RSP1B via SoapySDR. Outputs USB-demodulated WAV."""
import sys
import numpy as np
import SoapySDR
import wave
import struct

def record_fax(freq_hz, duration_sec, outfile):
    """Record and USB-demodulate a radiofax signal."""
    SAMP_RATE = 250000  # RSP1B minimum ~62500, use 250k for good fax quality
    # Radiofax uses USB, tune 1.9 kHz below assigned freq
    tune_freq = freq_hz - 1900

    print("Recording: freq=%d Hz, tune=%d Hz, duration=%ds" % (freq_hz, tune_freq, duration_sec))

    # Open SDRplay RSP1B
    args = SoapySDR.KwargsFromString("driver=sdrplay")
    sdr = SoapySDR.Device(args)
    sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, SAMP_RATE)
    sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, tune_freq)
    sdr.setGainMode(SoapySDR.SOAPY_SDR_RX, 0, False)  # Disable AGC
    sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 40)

    # Setup stream
    rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    sdr.activateStream(rxStream)

    total_samples = int(SAMP_RATE * duration_sec)
    buf_size = 4096
    buf = np.zeros(buf_size, dtype=np.complex64)
    audio_samples = []
    collected = 0

    print("Collecting %d samples..." % total_samples)

    while collected < total_samples:
        sr = sdr.readStream(rxStream, [buf], buf_size)
        if sr.ret > 0:
            iq = buf[:sr.ret]
            # USB demodulation: take real part of analytic signal
            # Simple approach: just take the real component (works for narrow USB)
            audio = np.real(iq)
            # Normalize
            audio = audio / (np.max(np.abs(audio)) + 1e-10)
            audio_samples.extend(audio.tolist())
            collected += sr.ret

    sdr.deactivateStream(rxStream)
    sdr.closeStream(rxStream)

    print("Collected %d samples at %d Hz, downsampling to 11025 Hz..." % (len(audio_samples), SAMP_RATE))

    # Downsample to 11025 Hz for fax decoder
    OUT_RATE = 11025
    audio_np = np.array(audio_samples, dtype=np.float32)
    # Simple decimation
    ratio = SAMP_RATE / OUT_RATE
    indices = np.arange(0, len(audio_np), ratio).astype(int)
    indices = indices[indices < len(audio_np)]
    downsampled = audio_np[indices]
    # Normalize
    peak = np.max(np.abs(downsampled))
    if peak > 0:
        downsampled = downsampled / peak

    # Write WAV
    with wave.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(OUT_RATE)
        for s in downsampled:
            wf.writeframes(struct.pack('<h', int(max(-1, min(1, float(s))) * 32767)))

    print("Saved: %s" % outfile)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: wxfax-record.py freq_hz duration_sec output.wav")
        sys.exit(1)
    record_fax(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
