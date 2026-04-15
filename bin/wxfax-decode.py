#!/usr/bin/env python3
"""Simple radiofax decoder - converts WAV audio to PNG image."""
import sys
import wave
import struct
import math
from PIL import Image

def decode_fax(wavfile, outfile):
    """Decode a radiofax WAV file to a PNG image."""
    # Radiofax parameters
    LPM = 120  # Lines per minute (standard)
    IOC = 576  # Index of Cooperation (standard for weather fax)

    # Read WAV file
    with wave.open(wavfile, 'r') as wf:
        nchannels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    # Convert to float samples
    if sampwidth == 2:
        fmt = "<%dh" % (nframes * nchannels)
        samples = struct.unpack(fmt, raw)
        if nchannels == 2:
            samples = samples[::2]  # Take left channel
        samples = [s / 32768.0 for s in samples]
    elif sampwidth == 1:
        samples = [struct.unpack('B', raw[i:i+1])[0] / 128.0 - 1.0 for i in range(0, len(raw), nchannels)]
    else:
        print("Unsupported sample width: %d" % sampwidth)
        return False

    print("WAV: %d Hz, %d samples, %.1f seconds" % (framerate, len(samples), len(samples) / framerate))

    # Radiofax demodulation
    # The fax signal is AM-modulated on a 2400 Hz subcarrier
    # Black = 1500 Hz, White = 2300 Hz (IOC 576)

    samples_per_line = int(framerate * 60 / LPM)
    pixels_per_line = IOC * math.pi  # ~1810 pixels per line
    pixels_per_line = int(pixels_per_line)

    total_lines = len(samples) // samples_per_line

    if total_lines < 10:
        print("Too few lines (%d), audio may be too short" % total_lines)
        return False

    print("Decoding: %d lines, %d pixels/line" % (total_lines, pixels_per_line))

    # Create image
    img = Image.new('L', (pixels_per_line, total_lines), 128)

    # Demodulate each line
    for line in range(total_lines):
        start = line * samples_per_line
        end = start + samples_per_line
        line_samples = samples[start:end]

        # Resample to pixels_per_line
        for px in range(pixels_per_line):
            idx = int(px * len(line_samples) / pixels_per_line)
            if idx >= len(line_samples) - 1:
                break

            # Simple envelope detection - compute instantaneous frequency
            # Using zero-crossing rate in a small window
            window = 32
            si = max(0, min(idx, len(line_samples) - window))
            segment = line_samples[si:si + window]

            # Count zero crossings
            crossings = 0
            for i in range(1, len(segment)):
                if segment[i-1] * segment[i] < 0:
                    crossings += 1

            # Estimate frequency from zero crossings
            freq_est = crossings * framerate / (2 * window)

            # Map frequency to grayscale (1500 Hz = black, 2300 Hz = white)
            brightness = (freq_est - 1500) / (2300 - 1500)
            brightness = max(0.0, min(1.0, brightness))
            pixel = int(brightness * 255)

            img.putpixel((px, line), pixel)

    # Save
    img.save(outfile)
    print("Saved: %s (%dx%d)" % (outfile, pixels_per_line, total_lines))
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: wxfax-decode.py input.wav output.png")
        sys.exit(1)

    success = decode_fax(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
