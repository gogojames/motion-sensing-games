"""Procedural rendering for the fruit-slicing game."""
from __future__ import annotations

import math
from typing import Any, Optional

from fruit_slicing.entities import Bomb, Fruit, FruitSlicingState, HandBlade


def render_fruit(screen: Any, fruit: Fruit) -> None:
    """Render a fruit as a coloured circle with rotation indicator."""
    import pygame  # noqa: PLC0415

    color = fruit.type.color
    r = int(fruit.radius)
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, 220), (r, r), r)
    inner_color = tuple(min(255, c + 40) for c in color)
    pygame.draw.circle(surf, (*inner_color, 100), (r - r // 4, r - r // 4), r // 3)
    angle_rad = math.radians(fruit.rotation)
    ex = r + int(r * 0.7 * math.cos(angle_rad))
    ey = r + int(r * 0.7 * math.sin(angle_rad))
    pygame.draw.line(surf, (255, 255, 255, 180), (r, r), (ex, ey), 2)
    rotated = pygame.transform.rotate(surf, fruit.rotation)
    rect = rotated.get_rect(center=(int(fruit.x), int(fruit.y)))
    screen.blit(rotated, rect)


def render_bomb(screen: Any, bomb: Bomb) -> None:
    """Render a bomb as a dark spiky circle."""
    import pygame  # noqa: PLC0415

    r = int(bomb.radius)
    surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
    cx, cy = r + 5, r + 5
    pygame.draw.circle(surf, (40, 40, 40, 230), (cx, cy), r)
    for i in range(8):
        angle = math.radians(i * 45 + bomb.rotation)
        sx = cx + int(r * 0.8 * math.cos(angle))
        sy = cy + int(r * 0.8 * math.sin(angle))
        pygame.draw.circle(surf, (60, 60, 60, 200), (sx, sy), 6)
    pygame.draw.circle(surf, (255, 60, 60, 200), (cx, cy - r // 3), 4)
    rect = surf.get_rect(center=(int(bomb.x), int(bomb.y)))
    screen.blit(surf, rect)


def render_hand_blade(screen: Any, blade: HandBlade) -> None:
    """Render hand-blade swipe trail."""
    import pygame  # noqa: PLC0415

    if blade.lifetime <= 0:
        return
    alpha = min(255, blade.lifetime * 25)
    points = blade.arc if len(blade.arc) > 2 else [blade.start_pos, blade.end_pos]
    if len(points) >= 2:
        color = (100, 220, 255, alpha)
        for i in range(len(points) - 1):
            p1 = (int(points[i][0]), int(points[i][1]))
            p2 = (int(points[i + 1][0]), int(points[i + 1][1]))
            pygame.draw.line(screen, color[:3], p1, p2, 4)


def render_particles(
    screen: Any, particles: list[dict]
) -> None:
    """Render particle effects for slicing and explosions."""
    import pygame  # noqa: PLC0415

    for p in particles:
        alpha = max(0, int(p.get("life", 1.0) * 255))
        color = p.get("color", (255, 255, 255))
        size = max(1, int(p.get("size", 3)))
        pos = (int(p["x"]), int(p["y"]))
        if 0 <= pos[0] < screen.get_width() and 0 <= pos[1] < screen.get_height():
            pygame.draw.circle(screen, color, pos, size)


def render_hud(screen: Any, state: FruitSlicingState) -> None:
    """Render heads-up display: score, lives, combo, wave."""
    import pygame  # noqa: PLC0415

    w = screen.get_width()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)

    score_text = font.render(f"Score: {state.score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    for i in range(state.lives):
        pygame.draw.circle(screen, (255, 50, 50), (w - 30 - i * 35, 30), 12)

    if state.combo > 1:
        combo_text = font.render(f"Combo x{state.combo}", True, (255, 255, 100))
        screen.blit(combo_text, (w // 2 - combo_text.get_width() // 2, 20))

    wave_text = small_font.render(f"Wave {state.wave}", True, (180, 180, 180))
    screen.blit(wave_text, (20, 60))


def render_countdown(screen: Any, count: int) -> None:
    """Render the 3-2-1 countdown overlay."""
    import pygame  # noqa: PLC0415

    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    font = pygame.font.Font(None, 128)
    text = font.render(str(count), True, (255, 255, 255))
    screen.blit(text, (w // 2 - text.get_width() // 2, h // 2 - 64))


def render_game_over(screen: Any, state: FruitSlicingState) -> None:
    """Render game-over screen with final score."""
    import pygame  # noqa: PLC0415

    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    title_font = pygame.font.Font(None, 72)
    text = title_font.render("Game Over", True, (255, 80, 80))
    screen.blit(text, (w // 2 - text.get_width() // 2, h // 3))
    score_font = pygame.font.Font(None, 48)
    st = score_font.render(f"Score: {state.score}", True, (255, 255, 255))
    screen.blit(st, (w // 2 - st.get_width() // 2, h // 2))
    hint = pygame.font.Font(None, 32).render(
        "Press R to restart or Esc to quit", True, (180, 180, 180)
    )
    screen.blit(hint, (w // 2 - hint.get_width() // 2, h * 2 // 3))


def render_background(screen: Any, camera_frame: Any) -> None:
    """Render mirrored webcam feed as background."""
    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    import pygame  # noqa: PLC0415

    rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    rgb = np.flipud(rgb)
    rgb = np.fliplr(rgb)
    surf = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
    surf = pygame.transform.scale(surf, screen.get_size())
    screen.blit(surf, (0, 0))
