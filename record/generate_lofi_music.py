import math
import struct
import random

SAMPLE_RATE = 44100
DURATION = 120  # seconds
BPM = 85
BEAT_SEC = 60.0 / BPM

# Chord frequencies in Hz (Cmaj7 -> Am7 -> Dm7 -> G7)
CHORDS = [
    [261.63, 329.63, 392.00, 493.88],  # Cmaj7
    [220.00, 261.63, 329.63, 392.00],  # Am7
    [146.83, 174.61, 220.00, 261.63],  # Dm7
    [196.00, 246.94, 293.66, 349.23],  # G7
]

def generate_lofi_wav(filename="lofi_track.wav"):
    total_samples = int(SAMPLE_RATE * DURATION)
    samples = [0.0] * total_samples
    
    # 1. Add Chord synth pads
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        measure = (t / (BEAT_SEC * 4))
        chord_idx = int(measure) % len(CHORDS)
        chord_t = t % (BEAT_SEC * 4)
        
        # Soft envelope per chord
        env = min(1.0, chord_t / 0.1) * max(0.0, 1.0 - (chord_t / (BEAT_SEC * 4)))
        
        chord_val = 0.0
        for freq in CHORDS[chord_idx]:
            # Warm sine + gentle warm harmonic
            val = math.sin(2 * math.pi * freq * t) * 0.5 + math.sin(2 * math.pi * (freq * 2) * t) * 0.15
            chord_val += val
            
        samples[i] += chord_val * 0.12 * env

    # 2. Add Kick and Snare Lo-Fi Drums
    total_beats = int(DURATION / BEAT_SEC)
    for b in range(total_beats):
        beat_start = int(b * BEAT_SEC * SAMPLE_RATE)
        pattern_step = b % 4
        
        # Kick on beat 0 and beat 2.5
        is_kick = (pattern_step == 0) or (pattern_step == 2)
        # Snare on beat 1 and 3
        is_snare = (pattern_step == 1) or (pattern_step == 3)
        
        if is_kick:
            kick_len = int(SAMPLE_RATE * 0.18)
            for k in range(kick_len):
                idx = beat_start + k
                if idx < total_samples:
                    kt = k / SAMPLE_RATE
                    # Pitch drop kick 120Hz -> 45Hz
                    freq = 120.0 * math.exp(-kt * 25.0) + 45.0
                    env = math.exp(-kt * 18.0)
                    samples[idx] += math.sin(2 * math.pi * freq * kt) * 0.45 * env
                    
        if is_snare:
            snare_len = int(SAMPLE_RATE * 0.15)
            for s in range(snare_len):
                idx = beat_start + s
                if idx < total_samples:
                    st = s / SAMPLE_RATE
                    noise = (random.random() * 2.0 - 1.0) * 0.25
                    tone = math.sin(2 * math.pi * 180.0 * st) * 0.2
                    env = math.exp(-st * 22.0)
                    samples[idx] += (noise + tone) * 0.35 * env

    # 3. Add Vinyl Crackle / Soft White Noise Background
    for i in range(total_samples):
        if random.random() < 0.002: # Vinyl pop
            samples[i] += (random.random() * 2.0 - 1.0) * 0.08
        samples[i] += (random.random() * 2.0 - 1.0) * 0.008 # White noise floor

    # Normalize & pack to 16-bit WAV PCM
    max_val = max(abs(s) for s in samples) or 1.0
    scale = 28000.0 / max_val
    
    with open(filename, "wb") as f:
        # Write WAV Header
        num_channels = 1
        bytes_per_sample = 2
        block_align = num_channels * bytes_per_sample
        byte_rate = SAMPLE_RATE * block_align
        data_size = total_samples * block_align
        
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_size, b"WAVE",
            b"fmt ", 16, 1, num_channels,
            SAMPLE_RATE, byte_rate, block_align, 16,
            b"data", data_size
        )
        f.write(header)
        for s in samples:
            f.write(struct.pack("<h", int(s * scale)))

if __name__ == "__main__":
    generate_lofi_wav()
    print("Generated lofi_track.wav")
