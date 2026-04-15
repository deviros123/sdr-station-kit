#!/usr/bin/env python3
"""Record radiofax audio from RSP1B via SoapySDR. Outputs USB-demodulated WAV."""
import sys
import numpy as np
import SoapySDR
import wave
import struct

def record_fax(freq_hz, duration_sec, outfile):
    """Record and USB-demodulate a radiofax signal."""
    SAMP_RATE = 48000
    # Radiofax uses USB, tune 1.9 kHz below assigned freq
    tune_freq = freq_hz - 1900

    print("Recording: freq=%d Hz, tune=%d Hz, duration=%ds" % (freq_hz, tune_freq, duration_sec))

    # Open SDRplay RSP1B
    args = dict(driver="sdrplay")
    sdr = SoapySDR.Device(args)
    sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, SAMP_RATE)
    sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, tune_freq)
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

    print("Collected %d samples, writing WAV..." % len(audio_samples))

    # Write WAV
    with wave.open(outfile, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMP_RATE)
        for s in audio_samples:
            wf.writeframes(struct.pack('<h', int(max(-1, min(1, s)) * 32767)))

    print("Saved: %s" % outfile)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: wxfax-record.py freq_hz duration_sec output.wav")
        sys.exit(1)
    record_fax(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
