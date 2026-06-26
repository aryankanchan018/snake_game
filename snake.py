# =============================================================================
# snake.py — Snake entity: movement, growth, rendering, collision
# =============================================================================

import pygame
import math
from constants import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    SNAKE_SKINS,
)


class Snake:
    """
    Represents the player-controlled snake.

    Grid coordinates are (col, row) integers.
    The body is a list of (col, row) tuples; index 0 is the head.
    """

    def __init__(self, skin: str = "Classic"):
        self.skin = skin
        self.reset()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def reset(self):
        """Re-initialise to a 3-segment snake in the centre of the grid."""
        start_col = GRID_COLS // 2
        start_row = GRID_ROWS // 2
        # Head at centre, body extends to the left
        self.body: list[tuple[int, int]] = [
            (start_col,     start_row),
            (start_col - 1, start_row),
            (start_col - 2, start_row),
        ]
        self.direction  = (1, 0)   # moving right
        self._next_dir  = (1, 0)   # buffered input direction
        self._grow       = 0        # segments to add on next move

    # ── Input ─────────────────────────────────────────────────────────────────

    def set_direction(self, dx: int, dy: int):
        """
        Buffer a new direction.  Ignores reversal (180°) to prevent self-collision.
        """
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self._next_dir = (dx, dy)

    # ── Update ────────────────────────────────────────────────────────────────

    def move(self) -> bool:
        """
        Advance the snake one step.
        Returns False if the snake collides with a wall or itself.
        """
        self.direction = self._next_dir
        head_col, head_row = self.body[0]
        new_head = (head_col + self.direction[0], head_row + self.direction[1])

        # Wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            return False

        # Self collision (skip the tail tip which will be removed)
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)
        if self._grow > 0:
            self._grow -= 1          # Keep the tail — snake grows
        else:
            self.body.pop()          # Remove the tail — normal move

        return True

    def grow(self, amount: int = 1):
        """Queue extra segments to be added over the next `amount` moves."""
        self._grow += amount

    # ── Queries ───────────────────────────────────────────────────────────────

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)

    def occupies(self, col: int, row: int) -> bool:
        return (col, row) in self.body

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, tick: int):
        """
        Draw the snake with a glow effect on the head and a gradient body.
        `tick` is used to animate the head pulse.
        """
        head_color, body_color, glow_color = SNAKE_SKINS[self.skin]
        total = len(self.body)

        for i, (col, row) in enumerate(self.body):
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

            if i == 0:  # ── Head ──────────────────────────────────────────
                self._draw_glow(surface, x, y, glow_color, tick)
                pygame.draw.rect(surface, head_color, rect, border_radius=6)
                # Eyes
                self._draw_eyes(surface, x, y)
            else:       # ── Body ──────────────────────────────────────────
                # Fade body toward tail
                t = i / max(total - 1, 1)
                color = _lerp_color(body_color, _darken(body_color, 0.45), t)
                pygame.draw.rect(surface, color, rect, border_radius=4)

    def _draw_glow(self, surface: pygame.Surface, x: int, y: int,
                   glow_color: tuple, tick: int):
        """Soft pulsing glow behind the head."""
        pulse = int(12 + 6 * math.sin(tick * 0.15))
        glow_surf = pygame.Surface((CELL_SIZE + pulse * 2, CELL_SIZE + pulse * 2),
                                   pygame.SRCALPHA)
        pygame.draw.ellipse(
            glow_surf,
            (*glow_color, 55),
            glow_surf.get_rect(),
        )
        surface.blit(glow_surf, (x - pulse, y - pulse))

    def _draw_eyes(self, surface: pygame.Surface, x: int, y: int):
        """Draw two small white pupils on the head."""
        dx, dy = self.direction
        cx = x + CELL_SIZE // 2
        cy = y + CELL_SIZE // 2

        # Offset eyes perpendicular to movement direction
        if dx != 0:  # horizontal movement
            offsets = [(dx * 4, -5), (dx * 4, 5)]
        else:        # vertical movement
            offsets = [(-5, dy * 4), (5, dy * 4)]

        for ox, oy in offsets:
            pygame.draw.circle(surface, WHITE, (cx + ox, cy + oy), 3)
            pygame.draw.circle(surface, BLACK, (cx + ox + dx, cy + oy + dy), 1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _darken(color, factor):
    return tuple(max(0, int(c * (1 - factor))) for c in color)
