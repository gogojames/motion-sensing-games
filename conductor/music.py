"""Procedural music engine for the conductor game."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class MusicLayer:
    """A single procedural audio layer."""
    name: str
    enabled: bool = False
    volume: float = 0.0
    waveform_type: str = "sine"
    frequency_range: tuple[float, float] = (200.0, 400.0)
    pattern: list[float] = field(default_factory=list)
    tempo_multiplier: float = 1.0
    _phase: float = 0.0


class MusicEngine:
    """Generates layered procedural music driven by conductor gestures."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self._sample_rate = sample_rate
        self._bpm: float = 120.0
        self._volume_amplitude: float = 0.5
        self._supernova_active = False
        self._supernova_timer: float = 0.0
        self._supernova_duration: float = 8.0
        self._position_sec: float = 0.0

        self._layers: dict[str, MusicLayer] = {
            "drums": MusicLayer(
                name="drums",
                waveform_type="noise",
                frequency_range=(60.0, 200.0),
                pattern=[0.0, 0.5],
                tempo_multiplier=1.0,
            ),
            "bass": MusicLayer(
                name="bass",
                waveform_type="saw",
                frequency_range=(60.0, 200.0),
                pattern=[0.0, 0.25, 0.5, 0.75],
                tempo_multiplier=0.5,
            ),
            "melody": MusicLayer(
                name="melody",
                waveform_type="sine",
                frequency_range=(400.0, 800.0),
                pattern=[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875],
                tempo_multiplier=2.0,
            ),
            "harmony": MusicLayer(
                name="harmony",
                waveform_type="square",
                frequency_range=(200.0, 400.0),
                pattern=[0.0, 0.333, 0.666],
                tempo_multiplier=1.0,
            ),
        }

        self._layer_activation_combos = {
            "drums": 5,
            "bass": 10,
            "melody": 20,
            "harmony": 30,
        }

    def set_tempo(self, bpm: float) -> None:
        """Set music tempo from conductor arm speed."""
        self._bpm = max(60.0, min(180.0, bpm))

    def set_volume(self, amplitude: float) -> None:
        """Set volume envelope from arm span."""
        self._volume_amplitude = max(0.0, min(1.0, amplitude))

    def activate_layer(self, layer_name: str) -> None:
        """Activate a music layer by name."""
        if layer_name in self._layers:
            self._layers[layer_name].enabled = True
            self._layers[layer_name].volume = 0.7

    def check_layer_activations(self, combo: int) -> list[str]:
        """Activate layers based on combo milestones. Returns names of newly activated layers."""
        activated: list[str] = []
        for name, threshold in self._layer_activation_combos.items():
            if combo >= threshold and not self._layers[name].enabled:
                self.activate_layer(name)
                activated.append(name)
        return activated

    def trigger_supernova(self) -> None:
        """Trigger 8-second supernova burst."""
        self._supernova_active = True
        self._supernova_timer = self._supernova_duration
        for layer in self._layers.values():
            layer.enabled = True
            layer.volume = 1.0

    def update(self, dt: float) -> None:
        """Advance playback position and manage supernova timer."""
        self._position_sec += dt
        if self._supernova_active:
            self._supernova_timer -= dt
            if self._supernova_timer <= 0:
                self._supernova_active = False
                self._supernova_timer = 0.0

    def render_buffer(self, num_samples: int) -> Optional[np.ndarray]:
        """Render mixed audio buffer. Returns int16 array or None if nothing enabled."""
        any_enabled = any(l.enabled for l in self._layers.values())
        if not any_enabled:
            return None

        sr = self._sample_rate
        mix = np.zeros(num_samples, dtype=np.float64)

        for layer in self._layers.values():
            if not layer.enabled or layer.volume <= 0:
                continue

            freq_low, freq_high = layer.frequency_range
            tempo_factor = self._bpm / 120.0 * layer.tempo_multiplier
            beat_duration = (60.0 / self._bpm) / layer.tempo_multiplier

            for i in range(num_samples):
                t = self._position_sec + i / sr

                if layer.waveform_type == "noise":
                    wave = np.random.uniform(-1.0, 1.0)
                    in_beat = any(
                        abs((t * tempo_factor) % beat_duration - p * beat_duration) < 0.02
                        for p in layer.pattern
                    )
                    wave *= 0.5 if in_beat else 0.05
                else:
                    freq = freq_low + (freq_high - freq_low) * 0.5
                    phase = 2.0 * math.pi * freq * t + layer._phase

                    if layer.waveform_type == "sine":
                        wave = math.sin(phase)
                    elif layer.waveform_type == "square":
                        wave = 1.0 if math.sin(phase) > 0 else -1.0
                    elif layer.waveform_type == "saw":
                        wave = 2.0 * ((freq * t) % 1.0) - 1.0
                    else:
                        wave = math.sin(phase)

                    in_beat = any(
                        abs((t * tempo_factor) % beat_duration - p * beat_duration) < 0.02
                        for p in layer.pattern
                    )
                    wave *= 0.6 if in_beat else 0.1

                if self._supernova_active:
                    sf = freq_low + (freq_high - freq_low) * ((t * 4.0) % 1.0)
                    wave += 0.3 * math.sin(2.0 * math.pi * sf * t)

                mix[i] += wave * layer.volume * self._volume_amplitude

        max_abs = np.max(np.abs(mix))
        if max_abs > 1.0:
            mix /= max_abs

        return (mix * 32767 * 0.8).astype(np.int16)

    def update_position_from_gesture(self, arm_speed: float) -> None:
        """Map conductor arm speed to BPM. arm_speed in pixels/sec."""
        bpm = 80.0 + arm_speed * 0.3
        self.set_tempo(bpm)
