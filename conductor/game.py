"""Main game loop and state machine for the conductor game."""
from __future__ import annotations

import time
from typing import Any, Optional

import numpy as np

from common.scores import ScoreManager
from common.skeleton import render_skeleton
from conductor.gesture import ConductorGestureClassifier
from conductor.music import MusicEngine
from conductor.renderer import ConductorRenderer
from conductor.scoring import ConductorScorer
from conductor.targets import Choreography, StarNote, generate_choreography
from pose.landmarks import GestureType


class ConductorGame:
    """Rhythm conductor game with state machine and 60 fps loop."""

    TRACK_DURATION = 120.0

    def run(
        self,
        pose_thread: Any,
        screen: Any,
        scores: ScoreManager,
        sound_enabled: bool = True,
    ) -> None:
        """Run the conductor game until the player returns to menu."""
        import pygame  # noqa: PLC0415

        w, h = screen.get_width(), screen.get_height()
        clock = pygame.time.Clock()
        renderer = ConductorRenderer(w, h)
        music = MusicEngine()
        scorer = ConductorScorer()
        choreography = generate_choreography(self.TRACK_DURATION, screen_width=w, screen_height=h)

        phase = "countdown"
        gesture_classifier = ConductorGestureClassifier()
        track_position: float = 0.0
        countdown_start: float = 0.0
        prev_pose: Any = None
        prev_time: float = time.monotonic()
        detected_gesture: Optional[str] = None
        gesture_timer: float = 0.0
        music_position: float = 0.0

        audio_buffer_size = 2048
        audio_stream: Optional[Any] = None

        running = True
        while running:
            now = time.monotonic()
            dt = now - prev_time
            prev_time = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if phase == "result":
                            phase = "menu"

            frame = pose_thread.get_pose()
            camera_frame = frame.frame if frame is not None else None

            if phase == "countdown":
                elapsed = now - countdown_start
                count = 3 - int(elapsed)
                if count <= 0:
                    phase = "playing"
                    track_position = 0.0
                    music_position = 0.0
                else:
                    screen.fill((0, 0, 20))
                    renderer.render_starfield(screen, dt)
                    if frame is not None:
                        render_skeleton(screen, frame.landmarks, w, h)
                    font = pygame.font.Font(None, 120)
                    text = font.render(str(count), True, (255, 255, 255))
                    screen.blit(text, (w // 2 - text.get_width() // 2, h // 2 - 60))
                    pygame.display.flip()
                    clock.tick(60)
                    continue

            elif phase == "playing":
                track_position += dt
                music_position += dt

                if track_position >= self.TRACK_DURATION:
                    phase = "result"
                    result = scorer.get_final_result()
                    from datetime import date  # noqa: PLC0415
                    result["date"] = date.today().isoformat()
                    scores.update_highscore("conductor", result)
                    continue

                remaining = self.TRACK_DURATION - track_position

                pose = pose_thread.get_pose()
                gesture = None
                if pose is not None:
                    gesture = gesture_classifier.classify(pose.landmarks, now, dt, w, h)

                if gesture is not None:
                    detected_gesture = gesture.type.value if hasattr(gesture.type, 'value') else str(gesture.type)
                    gesture_timer = 0.5

                    active_notes = choreography.get_active_notes()
                    for note in active_notes:
                        if note.time_remaining <= 0.3:
                            timing = max(0.0, 1.0 - abs(note.time_remaining) / 0.3)
                            gesture_matches = _gesture_matches_note(gesture.type, note.target_type)
                            if gesture_matches and not note.hit:
                                note.hit = True
                                pts = scorer.on_hit(note.target_type, timing)
                                newly_activated = music.check_layer_activations(scorer.combo)
                                if scorer.supernova_active and not music._supernova_active:
                                    music.trigger_supernova()

                if gesture is None:
                    for note in choreography.get_active_notes():
                        if note.time_remaining < -0.5 and not note.hit:
                            note.missed = True
                            scorer.on_miss()

                arm_speed = 0.0
                if pose is not None and prev_pose is not None:
                    wrist_l = pose.landmarks[15]
                    wrist_r = pose.landmarks[16]
                    prev_wrist_l = prev_pose.landmarks[15]
                    prev_wrist_r = prev_pose.landmarks[16]
                    dx = (wrist_l[0] - prev_wrist_l[0]) + (wrist_r[0] - prev_wrist_r[0])
                    dy = (wrist_l[1] - prev_wrist_l[1]) + (wrist_r[1] - prev_wrist_r[1])
                    arm_speed = np.sqrt(dx * dx + dy * dy) / max(dt, 0.001) * 100
                if pose is not None:
                    prev_pose = pose

                music.update_position_from_gesture(arm_speed)
                music.set_volume(min(1.0, arm_speed / 300.0))
                music.update(dt)
                scorer.update_star_power(dt)

                for note in choreography.notes:
                    if note.visible:
                        note.time_remaining -= dt

                if gesture_timer > 0:
                    gesture_timer -= dt
                else:
                    detected_gesture = None

            screen.fill((0, 0, 20))
            renderer.render_starfield(screen, dt)

            if phase == "playing":
                if frame is not None:
                    render_skeleton(screen, frame.landmarks, w, h)
                for note in choreography.get_active_notes():
                    renderer.render_target_ring(screen, note.target_type, note.target_x, note.target_y, note.ring_radius)
                    renderer.render_star_note(screen, note)

                renderer.render_combo(screen, scorer.combo)
                renderer.render_star_power_meter(screen, scorer.star_power, scorer.supernova_active)
                renderer.render_gesture_indicator(screen, detected_gesture)
                renderer.render_hud(screen, scorer.score, remaining, sum(1 for l in music._layers.values() if l.enabled))

            elif phase == "result":
                result = scorer.get_final_result()
                renderer.render_rank_result(screen, result)

            pygame.display.flip()
            clock.tick(60)

        if audio_stream is not None:
            audio_stream.stop()


def _gesture_matches_note(gesture_type: Any, target_type: Any) -> bool:
    """Check if detected gesture matches the required target type."""
    mapping = {
        GestureType.LEFT_HAND_REACH: "LEFT_HAND",
        GestureType.RIGHT_HAND_REACH: "RIGHT_HAND",
        GestureType.DUAL_HAND_SYNC: "DUAL_HAND",
        GestureType.SQUAT: "SQUAT",
        GestureType.ARMS_EXTEND: "CONSTELLATION",
    }
    required = target_type.name if hasattr(target_type, 'name') else str(target_type)
    detected = mapping.get(gesture_type, str(gesture_type))
    return detected == required
