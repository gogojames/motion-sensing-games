"""Hand-blade collision detection for the fruit-slicing game."""
from __future__ import annotations

import math

from fruit_slicing.entities import Bomb, Fruit, HandBlade


def _point_to_segment_distance(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    """Minimum distance from point (px,py) to line segment (ax,ay)-(bx,by)."""
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-8:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def check_swipe_fruit(blade: HandBlade, fruit: Fruit) -> bool:
    """Check if a hand-blade swipe intersects a fruit."""
    if fruit.sliced or fruit.missed:
        return False
    ax, ay = blade.start_pos
    bx, by = blade.end_pos
    dist = _point_to_segment_distance(fruit.x, fruit.y, ax, ay, bx, by)
    return dist <= fruit.radius + 15


def check_swipe_bomb(blade: HandBlade, bomb: Bomb) -> bool:
    """Check if a hand-blade swipe intersects a bomb."""
    if bomb.exploded:
        return False
    ax, ay = blade.start_pos
    bx, by = blade.end_pos
    dist = _point_to_segment_distance(bomb.x, bomb.y, ax, ay, bx, by)
    return dist <= bomb.radius + 15


def check_fruit_missed(fruit: Fruit, screen_height: int) -> bool:
    """Check if a fruit has fallen off the bottom of the screen."""
    return fruit.y > screen_height + fruit.radius * 2
