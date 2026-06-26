# =============================================================================
# food.py — Food, GoldenFood, and PowerUp collectible entities
# =============================================================================

import pygame
import random
import math
from constants import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    FOOD_COLOR, FOOD_GLOW, GOLDEN_COLOR, GOLDEN_GLOW,
    PU_SPEED_COLOR, PU_SLOW_COLOR, PU_DOUBLE_COLOR,
)


class Food:
    """Standard red food that grows the snake and awards points."""

    def __init__(self, occupied: list[tuple[int, int]]):
        self.pos = self._random_pos(occupied)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _random_pos(occupied: list[tuple[int, int]]) -> tuple[int, int]:
        """Pick a grid cell that is not occupied by the snake."""
        free = [
            (c, r)
            for c in range(GRID_COLS)
            for r in range(GRID_ROWS)
            if (c, r) not in occupied
        ]
        return random.choice(free) if free else (0, 0)

    def respawn(self, occupied: list[tuple[int, int]]):
        self.pos = self._random_pos(occupied)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

        # Pulsing glow
        pulse = int(8 + 4 * math.sin(tick * 0.12))
        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, FOOD_GLOW, 60)

        # Main circle
        pygame.draw.circle(surface, FOOD_COLOR, (cx, cy), CELL_SIZE // 2 - 2)
        # Shine
        pygame.draw.circle(surface, (255, 180, 180), (cx - 3, cy - 3), 3)


class GoldenFood(Food):
    """
    Golden food that appears every N normal foods eaten.
    Awards more points and has a special shimmer animation.
    """

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

        # Larger, shinier glow
        pulse = int(10 + 6 * math.sin(tick * 0.1))
        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, GOLDEN_GLOW, 80)

        # Star shape via rotating polygon points
        num_pts = 8
        outer_r = CELL_SIZE // 2 - 1
        inner_r = outer_r // 2
        pts = []
        for k in range(num_pts * 2):
            angle = math.pi * k / num_pts - math.pi / 2 + tick * 0.03
            r = outer_r if k % 2 == 0 else inner_r
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, GOLDEN_COLOR, pts)
        pygame.draw.circle(surface, (255, 255, 180), (cx - 2, cy - 2), 3)


# ── Power-ups ─────────────────────────────────────────────────────────────────

PU_TYPES = ["speed", "slow", "double"]

_PU_META = {
    "speed":  (PU_SPEED_COLOR,  "⚡", "SPEED BOOST"),
    "slow":   (PU_SLOW_COLOR,   "❄",  "SLOW MOTION"),
    "double": (PU_DOUBLE_COLOR, "×2", "DOUBLE SCORE"),
}


class PowerUp(Food):
    """
    A randomly-typed power-up that floats on the grid.
    Types: 'speed', 'slow', 'double'
    """

    def __init__(self, occupied: list[tuple[int, int]]):
        self.kind = random.choice(PU_TYPES)
        super().__init__(occupied)

    def draw(self, surface: pygame.Surface, tick: int):
        col, row = self.pos
        cx = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

        color, label, _ = _PU_META[self.kind]

        # Rotating glow ring
        pulse = int(10 + 5 * math.sin(tick * 0.15))
        _draw_glow_circle(surface, cx, cy, pulse + CELL_SIZE // 2, color, 70)

        # Diamond shape
        r = CELL_SIZE // 2 - 1
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, WHITE, pts, 1)

        # Label (rendered each frame — small font; cache not needed at 60fps)
        font = pygame.font.SysFont("consolas", 11, bold=True)
        text = font.render(label, True, WHITE)
        surface.blit(text, text.get_rect(center=(cx, cy)))


# ── Helper ────────────────────────────────────────────────────────────────────

def _draw_glow_circle(surface, cx, cy, radius, color, alpha):
    """Draw a soft circular glow using an SRCALPHA surface."""
    size = radius * 2 + 4
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (size // 2, size // 2), radius)
    surface.blit(s, (cx - size // 2, cy - size // 2))
