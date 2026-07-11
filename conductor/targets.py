"""Star note targets and choreography for the conductor game."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class StarTargetType(Enum):
    """Target types with associated color and base point value."""
    LEFT_HAND = ("cyan", (0, 255, 255), 10)
    RIGHT_HAND = ("orange", (255, 165, 0), 10)
    DUAL_HAND = ("purple", (128, 0, 128), 25)
    SQUAT = ("gold", (255, 215, 0), 30)
    CONSTELLATION = ("white", (255, 255, 255), 20)

    def __init__(self, display: str, color: tuple[int, int, int], base_points: int) -> None:
        self.display_name = display
        self.color = color
        self.base_points = base_points


@dataclass
class StarNote:
    """A single approaching note target in the conductor game."""
    id: int
    target_type: StarTargetType
    approach_duration: float
    time_remaining: float
    target_x: float
    target_y: float
    ring_radius: float
    hit: bool = False
    missed: bool = False
    score_bonus: int = 0

    @property
    def progress(self) -> float:
        """How far along the approach (0.0 = just appeared, 1.0 = at ring)."""
        if self.approach_duration <= 0:
            return 1.0
        return max(0.0, 1.0 - (self.time_remaining / self.approach_duration))

    @property
    def visible(self) -> bool:
        return not self.hit and not self.missed and self.time_remaining > 0


@dataclass
class Choreography:
    """Pre-composed sequence of notes for the ~2 minute 'Star Voyage' track."""
    notes: List[StarNote] = field(default_factory=list)
    tempo_bpm: float = 120.0
    track_name: str = "Star Voyage"

    def get_notes_at_time(self, position_sec: float, window_sec: float = 3.0) -> list[StarNote]:
        """Return notes whose approach window includes the current position."""
        results: list[StarNote] = []
        for note in self.notes:
            note_start = note.approach_duration
            if (position_sec - window_sec) <= note_start <= (position_sec + window_sec):
                results.append(note)
        return results

    def get_active_notes(self) -> list[StarNote]:
        """Return all notes that are still visible (not hit/missed/expired)."""
        return [n for n in self.notes if n.visible]


def generate_choreography(
    track_duration_sec: float = 120.0,
    tempo_bpm: float = 120.0,
    screen_width: int = 1280,
    screen_height: int = 720,
) -> Choreography:
    """Generate the 'Star Voyage' choreography with progressive difficulty."""
    import numpy as np  # noqa: PLC0415

    notes: list[StarNote] = []
    beat_interval = 60.0 / tempo_bpm
    note_id = 0

    segment_duration = track_duration_sec / 4

    for seg in range(4):
        seg_start = seg * segment_duration
        seg_beats = int(segment_duration / beat_interval)

        if seg == 0:
            types = [StarTargetType.LEFT_HAND, StarTargetType.RIGHT_HAND]
            density = 0.5
        elif seg == 1:
            types = [StarTargetType.LEFT_HAND, StarTargetType.RIGHT_HAND, StarTargetType.DUAL_HAND]
            density = 0.65
        elif seg == 2:
            types = list(StarTargetType)
            density = 0.75
        else:
            types = list(StarTargetType)
            density = 0.85

        for beat in range(seg_beats):
            if np.random.random() > density:
                continue

            t = seg_start + beat * beat_interval
            target_type = types[np.random.randint(0, len(types))]

            positions = {
                StarTargetType.LEFT_HAND: (screen_width * 0.25, screen_height * 0.45),
                StarTargetType.RIGHT_HAND: (screen_width * 0.75, screen_height * 0.45),
                StarTargetType.DUAL_HAND: (screen_width * 0.50, screen_height * 0.35),
                StarTargetType.SQUAT: (screen_width * 0.50, screen_height * 0.70),
                StarTargetType.CONSTELLATION: (screen_width * 0.50, screen_height * 0.30),
            }

            tx, ty = positions[target_type]
            tx += np.random.uniform(-50, 50)
            ty += np.random.uniform(-30, 30)

            approach = 2.0 + (1.0 - seg / 3) * 1.0

            notes.append(StarNote(
                id=note_id,
                target_type=target_type,
                approach_duration=approach,
                time_remaining=approach,
                target_x=tx,
                target_y=ty,
                ring_radius=40.0,
                score_bonus=target_type.base_points,
            ))
            note_id += 1

    notes.sort(key=lambda n: n.approach_duration)
    return Choreography(notes=notes, tempo_bpm=tempo_bpm)
