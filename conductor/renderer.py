"""Starfield and target rendering for the conductor game."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from conductor.targets import StarNote, StarTargetType


class ConductorRenderer:
    """Renders the conductor game's starfield, targets, and HUD."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self._w = screen_width
        self._h = screen_height
        self._stars: list[dict] = self._init_stars(150)
        self._trail_points: list[tuple[float, float, float]] = []

    def _init_stars(self, count: int) -> list[dict]:
        stars: list[dict] = []
        rng = np.random.default_rng(42)
        for _ in range(count):
            stars.append({
                "x": rng.uniform(0.0, 1.0),
                "y": rng.uniform(0.0, 1.0),
                "z": rng.uniform(0.1, 1.0),
                "brightness": rng.uniform(0.3, 1.0),
            })
        return stars

    def render_starfield(self, screen: object, dt: float) -> None:
        """Render z-depth star particles moving toward viewer."""
        import pygame  # noqa: PLC0415

        for star in self._stars:
            star["z"] -= dt * 0.3
            if star["z"] <= 0.01:
                star["z"] = 1.0
                star["x"] = np.random.uniform(0.0, 1.0)
                star["y"] = np.random.uniform(0.0, 1.0)

            sx = int((star["x"] - 0.5) * self._w / star["z"] + self._w / 2)
            sy = int((star["y"] - 0.5) * self._h / star["z"] + self._h / 2)

            if 0 <= sx < self._w and 0 <= sy < self._h:
                size = max(1, int((1.0 - star["z"]) * 4))
                alpha = int(star["brightness"] * (1.0 - star["z"]) * 255)
                color_val = min(255, alpha)
                pygame.draw.circle(screen, (color_val, color_val, color_val), (sx, sy), size)

    def render_target_ring(
        self,
        screen: object,
        target_type: StarTargetType,
        x: float,
        y: float,
        radius: float,
    ) -> None:
        """Render a colored target ring at the given position."""
        import pygame  # noqa: PLC0415

        color = target_type.color
        ring_surf = pygame.Surface((int(radius * 2 + 10), int(radius * 2 + 10)), pygame.SRCALPHA)
        center = (int(radius + 5), int(radius + 5))
        pygame.draw.circle(ring_surf, (*color, 180), center, int(radius), 3)
        pygame.draw.circle(ring_surf, (*color, 60), center, int(radius * 0.6))
        screen.blit(ring_surf, (int(x - radius - 5), int(y - radius - 5)))

    def render_star_note(
        self,
        screen: object,
        note: StarNote,
    ) -> None:
        """Render an approaching note growing toward its target ring."""
        import pygame  # noqa: PLC0415

        progress = note.progress
        start_x = self._w / 2
        start_y = self._h * 0.1
        cur_x = start_x + (note.target_x - start_x) * progress
        cur_y = start_y + (note.target_y - start_y) * progress
        cur_r = 5.0 + (note.ring_radius - 5.0) * progress

        color = note.target_type.color
        alpha = int(progress * 255)

        note_surf = pygame.Surface((int(cur_r * 2 + 4), int(cur_r * 2 + 4)), pygame.SRCALPHA)
        center = (int(cur_r + 2), int(cur_r + 2))
        draw_alpha = min(255, alpha)
        pygame.draw.circle(note_surf, (*color, draw_alpha), center, int(cur_r))
        screen.blit(note_surf, (int(cur_x - cur_r - 2), int(cur_y - cur_r - 2)))

        self._trail_points.append((cur_x, cur_y, progress))

    def render_gesture_indicator(
        self,
        screen: object,
        detected_gesture: Optional[str],
    ) -> None:
        """Show detected gesture as text feedback."""
        import pygame  # noqa: PLC0415

        if detected_gesture is None:
            return
        font = pygame.font.Font(None, 36)
        text = font.render(detected_gesture, True, (200, 200, 200))
        screen.blit(text, (self._w // 2 - text.get_width() // 2, 20))

    def render_star_power_meter(
        self,
        screen: object,
        star_power: float,
        supernova_active: bool,
    ) -> None:
        """Render star power bar."""
        import pygame  # noqa: PLC0415

        bar_w, bar_h = 200, 12
        bx = self._w - bar_w - 20
        by = 20

        pygame.draw.rect(screen, (40, 40, 40), (bx, by, bar_w, bar_h))
        fill_w = int(bar_w * min(1.0, star_power))
        color = (255, 215, 0) if not supernova_active else (255, 100, 100)
        pygame.draw.rect(screen, color, (bx, by, fill_w, bar_h))
        pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1)

    def render_combo(self, screen: object, combo: int) -> None:
        """Render combo counter."""
        import pygame  # noqa: PLC0415

        if combo <= 0:
            return
        font = pygame.font.Font(None, 60)
        text = font.render(f"{combo}x", True, (255, 255, 100))
        screen.blit(text, (self._w // 2 - text.get_width() // 2, 70))

    def render_rank_result(
        self,
        screen: object,
        result: dict,
    ) -> None:
        """Render final rank with large letter."""
        import pygame  # noqa: PLC0415

        screen.fill((0, 0, 20))

        rank = result.get("rank", "F")
        rank_colors = {
            "S": (255, 215, 0),
            "A": (0, 200, 255),
            "B": (0, 255, 100),
            "C": (255, 255, 0),
            "D": (255, 165, 0),
            "F": (200, 50, 50),
        }
        color = rank_colors.get(rank, (200, 200, 200))

        font_large = pygame.font.Font(None, 180)
        text = font_large.render(rank, True, color)
        screen.blit(text, (self._w // 2 - text.get_width() // 2, self._h // 2 - 120))

        font_med = pygame.font.Font(None, 48)
        score_text = font_med.render(f"Score: {result.get('score', 0)}", True, (255, 255, 255))
        screen.blit(score_text, (self._w // 2 - score_text.get_width() // 2, self._h // 2 + 40))

        combo_text = font_med.render(f"Max Combo: {result.get('max_combo', 0)}", True, (200, 200, 200))
        screen.blit(combo_text, (self._w // 2 - combo_text.get_width() // 2, self._h // 2 + 90))

        font_sm = pygame.font.Font(None, 32)
        hint = font_sm.render("Press Space or raise hands to return", True, (150, 150, 150))
        screen.blit(hint, (self._w // 2 - hint.get_width() // 2, self._h - 50))

    def render_hud(
        self,
        screen: object,
        score: int,
        time_remaining: float,
        layers_active: int,
    ) -> None:
        """Render score, time, and active layers."""
        import pygame  # noqa: PLC0415

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        minutes = int(time_remaining) // 60
        seconds = int(time_remaining) % 60
        time_text = font.render(f"{minutes}:{seconds:02d}", True, (200, 200, 200))
        screen.blit(time_text, (20, 55))

        layer_text = font.render(f"Layers: {layers_active}/4", True, (150, 150, 150))
        screen.blit(layer_text, (20, 90))

    def cleanup_trails(self) -> None:
        """Remove old trail points."""
        self._trail_points = [(x, y, p) for x, y, p in self._trail_points if p > 0.1]
