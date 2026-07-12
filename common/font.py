"""Font utilities with CJK support."""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import Any


_CJK_FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
    "C:\\Windows\\Fonts\\simhei.ttf",
]


@lru_cache(maxsize=1)
def _find_cjk_font() -> str | None:
    for path in _CJK_FONT_PATHS:
        if os.path.exists(path):
            return path
    return None


def get_font(size: int) -> Any:
    """Return a pygame font at the given size, using CJK-capable font if available."""
    import pygame  # noqa: PLC0415

    path = _find_cjk_font()
    if path is not None:
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)
