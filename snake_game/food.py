# =============================================================================
# snake_game/food.py — Food, GoldenFood, and PowerUp collectibles
# =============================================================================

import pygame
import random
import math
from typing import List, Tuple
from snake_game.constants import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    FOOD_COLOR, FOOD_GLOW, GOLDEN_COLOR, GOLDEN_GLOW,
    PU_SPEED_COLOR, PU_SLOW_COLOR, PU_DOUBLE_COLOR, WHITE,
)

# Power-up metadata: kind → (color, short_label, display_name)
PU_TYPES = ["speed", "slow", "double"]
_PU_META = {
    "speed":  (PU_SPEED_COLOR,  "SPD", "SPEED BOOST"),
    "slow":   (PU_SLOW_COLOR,   "SLO", "SLOW MOTION"),
    "double": (PU_DOUBLE_COLOR, "x2",  "DOUBLE SCORE"),
}

# Module-level font — initialised once after pygame.init()
_pu_font: pygame.font.Font = None

def _get_pu_font() -> pygame.font.Font:
    global _pu_font
    if _pu_font is None:
        _pu_font = pygame.font.SysFont("consolas", 11, bold=True)
    return _pu_font


class Food:
    """Standard food that grows the snake and awards base points."""

    def __init__(self, occupied: List[Tuple[int, int]]):
        self.pos = self._random_pos(occupied)

    @staticmethod
    def _random_pos(occupied: List[Tuple[int, int]]) -> Tuple[int, int]:
        free = [
            (c, r) for c in range(GRID_COLS) for r in range(GRID_ROWS)
            if (c, r) not in occupied
        ]
        return random.choice(free) if free else (0, 0)

    def respawn(self, occupied: List[Tuple[int, int]]):
        self.pos = self._random_pos(occupied)

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        pulse = int(8 + 4 * math.sin(tick * 0.12))
        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, FOOD_GLOW, 60)
        pygame.draw.circle(surface, FOOD_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
        pygame.draw.circle(surface, (255, 180, 180), (cx - 3, cy - 3), 3)


class GoldenFood(Food):
    """
    Rare golden food worth more points.
    Renders as a rotating 8-point star.
    """

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

        pulse    = int(10 + 6 * math.sin(tick * 0.1))
        outer_r  = CELL_SIZE // 2 - 1
        inner_r  = outer_r // 2
        num_pts  = 8

        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, GOLDEN_GLOW, 80)

        pts = []
        for k in range(num_pts * 2):
            angle = math.pi * k / num_pts - math.pi / 2 + tick * 0.03
            r = outer_r if k % 2 == 0 else inner_r
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, GOLDEN_COLOR, pts)
        pygame.draw.circle(surface, (255, 255, 180), (cx - 2, cy - 2), 3)


class PowerUp(Food):
    """
    Randomly-typed collectible granting a temporary effect.
    Types: 'speed' | 'slow' | 'double'
    """

    def __init__(self, occupied: List[Tuple[int, int]]):
        self.kind = random.choice(PU_TYPES)
        super().__init__(occupied)

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

        color, label, _ = _PU_META[self.kind]
        pulse = int(10 + 5 * math.sin(tick * 0.15))

        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, color, 70)

        # Diamond shape
        r   = CELL_SIZE // 2 - 1
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, WHITE, pts, 1)

        text = _get_pu_font().render(label, True, WHITE)
        surface.blit(text, text.get_rect(center=(cx, cy)))


# ── Shared helper ─────────────────────────────────────────────────────────────

def _draw_glow_circle(surface: pygame.Surface, cx: int, cy: int,
                      radius: int, color: tuple, alpha: int):
    size = radius * 2 + 4
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (size // 2, size // 2), radius)
    surface.blit(s, (cx - size // 2, cy - size // 2))
