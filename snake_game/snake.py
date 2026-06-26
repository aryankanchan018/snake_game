# =============================================================================
# snake_game/snake.py — Snake entity: movement, growth, rendering, collision
# =============================================================================

import pygame
import math
from typing import List, Tuple
from snake_game.constants import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    SNAKE_SKINS, WHITE, BLACK,
)


class Snake:
    """
    Player-controlled snake.

    Grid coordinates: (col, row) integers.
    Body is a list of (col, row) tuples; index 0 is the head.
    """

    def __init__(self, skin: str = "Classic"):
        self.skin = skin
        self.reset()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def reset(self):
        """Reinitialise a 3-segment snake at the grid centre."""
        sc = GRID_COLS // 2
        sr = GRID_ROWS // 2
        self.body: List[Tuple[int, int]] = [
            (sc,     sr),
            (sc - 1, sr),
            (sc - 2, sr),
        ]
        self.direction = (1, 0)   # moving right
        self._next_dir = (1, 0)
        self._grow     = 0

    # ── Input ─────────────────────────────────────────────────────────────────

    def set_direction(self, dx: int, dy: int):
        """Buffer a new direction; ignores 180° reversal."""
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self._next_dir = (dx, dy)

    # ── Update ────────────────────────────────────────────────────────────────

    def move(self) -> bool:
        """
        Advance one step.
        Returns False on wall or self collision (game over).
        """
        self.direction = self._next_dir
        hc, hr = self.body[0]
        new_head = (hc + self.direction[0], hr + self.direction[1])

        # Wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            return False

        # Self collision — exclude tail tip (it will move away unless growing)
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)
        if self._grow > 0:
            self._grow -= 1   # keep tail → snake grows
        else:
            self.body.pop()   # remove tail → normal move
        return True

    def grow(self, amount: int = 1):
        self._grow += amount

    # ── Queries ───────────────────────────────────────────────────────────────

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, tick: int):
        """Draw the snake with glowing head, gradient body, and eyes."""
        head_color, body_color, glow_color = SNAKE_SKINS[self.skin]
        total = len(self.body)

        for i, (col, row) in enumerate(self.body):
            x    = GRID_OFFSET_X + col * CELL_SIZE
            y    = GRID_OFFSET_Y + row * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

            if i == 0:
                self._draw_glow(surface, x, y, glow_color, tick)
                pygame.draw.rect(surface, head_color, rect, border_radius=6)
                self._draw_eyes(surface, x, y)
            else:
                t = i / max(total - 1, 1)
                color = _lerp_color(body_color, _darken(body_color, 0.45), t)
                pygame.draw.rect(surface, color, rect, border_radius=4)

    def _draw_glow(self, surface: pygame.Surface, x: int, y: int,
                   glow_color: tuple, tick: int):
        pulse = int(12 + 6 * math.sin(tick * 0.15))
        size  = CELL_SIZE + pulse * 2
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*glow_color, 55), s.get_rect())
        surface.blit(s, (x - pulse, y - pulse))

    def _draw_eyes(self, surface: pygame.Surface, x: int, y: int):
        dx, dy = self.direction
        cx = x + CELL_SIZE // 2
        cy = y + CELL_SIZE // 2
        offsets = [(dx * 4, -5), (dx * 4, 5)] if dx != 0 else [(-5, dy * 4), (5, dy * 4)]
        for ox, oy in offsets:
            pygame.draw.circle(surface, WHITE, (cx + ox, cy + oy), 3)
            pygame.draw.circle(surface, BLACK, (cx + ox + dx, cy + oy + dy), 1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def _darken(color, factor):
    return tuple(max(0, int(c * (1 - factor))) for c in color)
