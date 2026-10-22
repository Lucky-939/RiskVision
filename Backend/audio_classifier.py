"""
RiskVision 2.0 - Real-Time Audio Distress & Scream Detection Pipeline
Calibrated for Windows WASAPI / DirectSound (48 kHz stereo input with mono downmixing).
Extracts:
1. live_volume_pct: Instantaneous sound volume (0% - 100%) for live mic feedback
2. distress_confidence: Acoustic scream / distress score based on MFCC & high-frequency centroid
"""

import threading
import time
import numpy as np
import sounddevice as sd
from scipy.fftpack import dct

class AudioDistressClassifier:
    def __init__(self, sample_rate=48000, channels=2, num_mfcc=13, num_filters=26):
        self.sample_rate = sample_rate
        self.channels = channels
        self.num_mfcc = num_mfcc
        self.num_filters = num_filters
        
        # Audio stream state
        self.running = False
        self.stream = None
        
        # Real-time Telemetry
        self.live_volume_pct = 0.0     # 0 to 100 for live mic meter
        self.current_confidence = 0.0  # 0.0 to 1.0 for scream detection
        self.current_energy = 0.0
        self.current_centroid = 0.0
        self.is_distress = False
        self.last_update_time = time.time()
        
        # Ambient floor adaptation
        self.ambient_energy = 0.005
        self.ambient_alpha = 0.95
        
        # Precompute Mel Filterbank for 48kHz
        self.mel_filters = self._build_mel_filterbank(self.sample_rate, n_fft=1024, n_filters=self.num_filters)

    def _hz_to_mel(self, hz):
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel):
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _build_mel_filterbank(self, sample_rate, n_fft=1024, n_filters=26, low_freq=150, high_freq=8000):
        low_mel = self._hz_to_mel(low_freq)
        high_mel = self._hz_to_mel(high_freq)
        mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
        hz_points = self._mel_to_hz(mel_points)
        bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
        
        filters = np.zeros((n_filters, n_fft // 2 + 1))
        for m in range(1, n_filters + 1):
            f_m_minus = bins[m - 1]
            f_m = bins[m]
            f_m_plus = bins[m + 1]
            
            for k in range(f_m_minus, f_m):
                if f_m != f_m_minus:
                    filters[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                if f_m_plus != f_m:
                    filters[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)
        return filters

    def extract_mfcc(self, signal, n_fft=1024):
        # Pre-emphasis
        emphasized = np.append(signal[0], signal[1:] - 0.97 * signal[:-1])
        window = np.hamming(len(emphasized))
        windowed = emphasized * window
        
        fft_mag = np.abs(np.fft.rfft(windowed, n=n_fft))
        power_spectrum = (fft_mag ** 2) / n_fft
        
        mel_energies = np.dot(self.mel_filters, power_spectrum[:self.mel_filters.shape[1]])
        mel_energies = np.where(mel_energies == 0, np.finfo(float).eps, mel_energies)
        log_mel_energies = np.log(mel_energies)
        
        mfcc = dct(log_mel_energies, type=2, axis=-1, norm='ortho')[:self.num_mfcc]
        return mfcc

    def calculate_spectral_centroid(self, signal, n_fft=1024):
        fft_mag = np.abs(np.fft.rfft(signal, n=n_fft))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / self.sample_rate)
        sum_mag = np.sum(fft_mag)
        if sum_mag < 1e-6:
            return 0.0
        return float(np.sum(freqs * fft_mag) / sum_mag)

    def process_audio(self, mono_signal):
        rms = float(np.sqrt(np.mean(mono_signal ** 2)))
        self.current_energy = rms
        
        # 1. Live Volume Meter (0 - 100%)
        # RMS of 0.05 is loud normal speaking, >0.15 is shouting
        vol_pct = np.clip((rms / 0.12) * 100.0, 0.0, 100.0)
        # Smooth volume
        self.live_volume_pct = round(float(0.7 * self.live_volume_pct + 0.3 * vol_pct), 1)

        # Ambient noise floor tracking
        if rms < self.ambient_energy * 1.5:
            self.ambient_energy = self.ambient_alpha * self.ambient_energy + (1 - self.ambient_alpha) * max(rms, 0.002)

        # 2. Spectral Centroid (pitch indicator)
        centroid = self.calculate_spectral_centroid(mono_signal)
        self.current_centroid = float(centroid)

        # 3. MFCC coefficients
        mfccs = self.extract_mfcc(mono_signal)

        # Distress scoring
        # Screams have high energy ratio + elevated centroid (above 1500 Hz)
        energy_ratio = rms / (self.ambient_energy + 1e-6)
        energy_score = np.clip((energy_ratio - 2.5) / 5.0, 0.0, 1.0)
        
        if centroid >= 1300.0:
            centroid_score = np.clip((centroid - 1300.0) / 2200.0, 0.0, 1.0)
        else:
            centroid_score = 0.0

        high_mfcc = np.mean(np.abs(mfccs[3:8])) if len(mfccs) >= 8 else 0.0
        mfcc_score = np.clip(high_mfcc / 12.0, 0.0, 1.0)

        # Raw scream confidence
        raw_conf = (0.50 * energy_score) + (0.35 * centroid_score) + (0.15 * mfcc_score)
        
        # Fast rise, smooth decay
        if raw_conf > self.current_confidence:
            self.current_confidence = round(float(raw_conf), 2)
        else:
            self.current_confidence = round(float(0.80 * self.current_confidence + 0.20 * raw_conf), 2)

        self.is_distress = bool(self.current_confidence >= 0.50)
        self.last_update_time = time.time()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        # Downmix stereo to mono
        if indata.shape[1] > 1:
            mono = np.mean(indata, axis=1, dtype=np.float32)
        else:
            mono = indata[:, 0].astype(np.float32)
        self.process_audio(mono)

    def start(self):
        if self.running:
            return
        self.running = True
        try:
            # Native 48000 Hz, stereo channels
            block_size = int(self.sample_rate * 0.25) # 250ms chunks for rapid response
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=block_size,
                callback=self._audio_callback
            )
            self.stream.start()
            print("[AudioDistressClassifier] Microphone listener started on native 48kHz stereo stream.")
        except Exception as e:
            print(f"[AudioDistressClassifier] Error starting mic: {e}")
            self.running = False

    def stop(self):
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        print("[AudioDistressClassifier] Microphone listener stopped.")

    def get_status(self):
        return {
            "mic_level": float(self.live_volume_pct),
            "distress_confidence": float(self.current_confidence),
            "is_distress": bool(self.is_distress),
            "spectral_centroid_hz": float(round(float(self.current_centroid), 1)),
            "rms_energy": float(round(float(self.current_energy), 4))
        }

# Global singleton
audio_engine = AudioDistressClassifier()

if __name__ == "__main__":
    print("Testing AudioDistressClassifier on native 48kHz for 4 seconds...")
    audio_engine.start()
    try:
        for _ in range(8):
            time.sleep(0.5)
            s = audio_engine.get_status()
            print(f"Mic Level: {s['mic_level']}% | Distress Conf: {s['distress_confidence']:.2f} | Centroid: {s['spectral_centroid_hz']}Hz")
    finally:
        audio_engine.stop()
