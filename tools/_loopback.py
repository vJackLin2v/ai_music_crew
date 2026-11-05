
import numpy as np, sounddevice as sd, soundfile as sf, multiprocessing as mp, time
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-read.wav"
data, sr = sf.read(WAV, dtype="float32")
IN_DEV, OUT_DEV = 12, 16

def player():
    d, s = sf.read(WAV, dtype="float32")
    sd.play(d, s, device=OUT_DEV, blocking=True)

if __name__ == "__main__":
    p = mp.Process(target=player); p.start()
    time.sleep(0.3)
    rec = sd.rec(int(sr*4), samplerate=sr, channels=1, device=IN_DEV, dtype="float32", blocking=True)
    p.join()
    peak = float(np.max(np.abs(rec))); rms = float(np.sqrt(np.mean(rec**2)))
    print(f"loopback peak={peak:.4f} rms={rms:.5f}")
    print("PASS" if peak > 0.01 else "FAIL: 静音")
