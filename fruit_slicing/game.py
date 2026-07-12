"""Main game loop and state machine for the fruit-slicing game."""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from common.scores import ScoreManager
from common.skeleton import render_skeleton
from fruit_slicing.audio import (
    init_audio,
    play_bomb_sound,
    play_combo_chime,
    play_golden_sound,
    play_menu_click,
    play_miss_sound,
    play_slice_sound,
    set_enabled,
)
from fruit_slicing.collision import check_fruit_missed, check_swipe_bomb, check_swipe_fruit
from fruit_slicing.entities import Bomb, FruitSlicingState, GamePhase, HandBlade
from fruit_slicing.renderer import (
    render_background,
    render_bomb,
    render_countdown,
    render_fruit,
    render_game_over,
    render_hand_blade,
    render_hud,
    render_particles,
)
from fruit_slicing.scoring import (
    calculate_final_score,
    on_bomb_hit,
    on_fruit_missed,
    on_fruit_sliced,
)
from fruit_slicing.spawner import generate_wave, spawn_fruits
from pose.landmarks import GestureEvent, GestureType, is_hand_blade


class FruitSlicingGame:
    """Fruit-slicing game with state machine and 60 fps loop."""

    def run(
        self,
        pose_thread: Any,
        screen: Any,
        scores: ScoreManager,
        sound_enabled: bool = True,
    ) -> None:
        """Run the fruit-slicing game until the player returns to menu."""
        import pygame  # noqa: PLC0415

        init_audio()
        set_enabled(sound_enabled)
        clock = pygame.time.Clock()
        state = FruitSlicingState()
        state.phase = GamePhase.COUNTDOWN
        fruits: list = []
        bombs: list[Bomb] = []
        blades: list[HandBlade] = []
        particles: list[dict] = []
        prev_pose: Any = None
        prev_time: float = time.monotonic()
        wave_timer: float = 0.0
        spawn_index: int = 0
        spawn_timer: float = 0.0
        wave_fruits: list = []
        countdown_start: float = 0.0
        last_combo_milestone: int = 0
        game_over_handled = False

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
                    elif event.key == pygame.K_p and state.phase == GamePhase.PLAYING:
                        state.phase = GamePhase.PAUSED
                    elif event.key == pygame.K_p and state.phase == GamePhase.PAUSED:
                        state.phase = GamePhase.PLAYING
                    elif event.key == pygame.K_r and state.phase == GamePhase.GAME_OVER:
                        state = FruitSlicingState()
                        state.phase = GamePhase.COUNTDOWN
                        fruits.clear()
                        bombs.clear()
                        blades.clear()
                        particles.clear()
                        game_over_handled = False
                        last_combo_milestone = 0

            frame = pose_thread.get_pose()
            camera_frame = frame.frame if frame is not None else None

            if state.phase == GamePhase.COUNTDOWN:
                elapsed = now - countdown_start
                count = 3 - int(elapsed)
                if count <= 0:
                    state.phase = GamePhase.PLAYING
                    wave = generate_wave(state.wave)
                    wave_fruits = spawn_fruits(
                        wave, screen.get_width(), screen.get_height(), state.golden_fruit_spawned
                    )
                    spawn_index = 0
                    spawn_timer = 0.0
                else:
                    screen.fill((0, 0, 0))
                    if frame is not None:
                        render_skeleton(screen, frame.landmarks, screen.get_width(), screen.get_height())
                    render_countdown(screen, count)
                    pygame.display.flip()
                    clock.tick(60)
                    continue

            elif state.phase == GamePhase.PLAYING:
                pose = pose_thread.get_pose()
                if pose is not None and prev_pose is not None:
                    swipe, velocity, hand = is_hand_blade(
                        prev_pose.landmarks,
                        pose.landmarks,
                        dt,
                        screen.get_width(),
                        screen.get_height(),
                    )
                    if swipe:
                        w, h = pose_thread.frame_dimensions
                        blade = HandBlade(
                            hand=hand,
                            start_pos=(pose.landmarks[15 if hand != "right" else 16, 0] * w,
                                       pose.landmarks[15 if hand != "right" else 16, 1] * h),
                            end_pos=(pose.landmarks[16 if hand != "right" else 15, 0] * w,
                                     pose.landmarks[16 if hand != "right" else 15, 1] * h),
                            velocity=velocity,
                        )
                        blades.append(blade)
                if pose is not None:
                    prev_pose = pose

                spawn_timer += dt
                if spawn_index < len(wave_fruits) and spawn_timer >= 0.5:
                    f = wave_fruits[spawn_index]
                    fruits.append(f)
                    spawn_index += 1
                    spawn_timer = 0.0

                if spawn_index >= len(wave_fruits) and not fruits and not bombs:
                    state.wave += 1
                    wave = generate_wave(state.wave)
                    wave_fruits = spawn_fruits(
                        wave, screen.get_width(), screen.get_height(), state.golden_fruit_spawned
                    )
                    spawn_index = 0
                    spawn_timer = 0.0

                for f in fruits:
                    f.x += f.vx
                    f.y += f.vy
                    f.vy += 0.15
                    f.rotation += f.rotation_speed
                    if len(f.trail) > 5:
                        f.trail.pop(0)
                    f.trail.append((f.x, f.y))
                    if not f.sliced and check_fruit_missed(f, screen.get_height()):
                        f.missed = True
                        on_fruit_missed(state)
                        play_miss_sound()

                for b in bombs:
                    b.x += b.vx
                    b.y += b.vy
                    b.vy += 0.15
                    b.rotation += b.rotation_speed

                for blade in blades:
                    for f in fruits:
                        if check_swipe_fruit(blade, f):
                            f.sliced = True
                            pts = on_fruit_sliced(state, f)
                            play_slice_sound()
                            if state.combo > 0 and state.combo % 5 == 0 and state.combo != last_combo_milestone:
                                play_combo_chime(state.combo)
                                last_combo_milestone = state.combo
                            for _ in range(8):
                                particles.append({
                                    "x": f.x + np.random.uniform(-20, 20),
                                    "y": f.y + np.random.uniform(-20, 20),
                                    "vx": np.random.uniform(-3, 3),
                                    "vy": np.random.uniform(-3, 3),
                                    "life": 1.0,
                                    "color": f.type.color,
                                    "size": int(np.random.uniform(2, 6)),
                                })
                    for b in bombs:
                        if check_swipe_bomb(blade, b):
                            b.exploded = True
                            on_bomb_hit(state)
                            play_bomb_sound()
                            for _ in range(15):
                                particles.append({
                                    "x": b.x + np.random.uniform(-30, 30),
                                    "y": b.y + np.random.uniform(-30, 30),
                                    "vx": np.random.uniform(-5, 5),
                                    "vy": np.random.uniform(-5, 5),
                                    "life": 1.0,
                                    "color": (255, 100, 0),
                                    "size": int(np.random.uniform(3, 8)),
                                })

                for blade in blades:
                    blade.lifetime -= 1
                blades = [b for b in blades if b.lifetime > 0]

                for p in particles:
                    p["x"] += p.get("vx", 0)
                    p["y"] += p.get("vy", 0)
                    p["life"] -= dt * 2
                particles = [p for p in particles if p["life"] > 0]

                fruits = [f for f in fruits if not f.sliced and not f.missed]
                bombs = [b for b in bombs if not b.exploded and b.y < screen.get_height() + 100]

                if state.lives <= 0:
                    state.phase = GamePhase.GAME_OVER
                    game_over_handled = False

            elif state.phase == GamePhase.GAME_OVER:
                if not game_over_handled:
                    final = calculate_final_score(state)
                    from datetime import date  # noqa: PLC0415

                    final["date"] = date.today().isoformat()
                    scores.update_highscore("fruit_slicing", final)
                    game_over_handled = True

            screen.fill((0, 0, 0))
            if state.phase in (GamePhase.PLAYING, GamePhase.PAUSED, GamePhase.GAME_OVER):
                render_background(screen, camera_frame)
                if frame is not None:
                    render_skeleton(screen, frame.landmarks, screen.get_width(), screen.get_height())
                for f in fruits:
                    render_fruit(screen, f)
                for b in bombs:
                    render_bomb(screen, b)
                for blade in blades:
                    render_hand_blade(screen, blade)
                render_particles(screen, particles)
                render_hud(screen, state)

            if state.phase == GamePhase.PAUSED:
                import pygame  # noqa: PLC0415

                font = pygame.font.Font(None, 72)
                text = font.render("PAUSED", True, (255, 255, 255))
                screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                                   screen.get_height() // 2 - 36))

            if state.phase == GamePhase.GAME_OVER:
                render_game_over(screen, state)

            pygame.display.flip()
            clock.tick(60)
