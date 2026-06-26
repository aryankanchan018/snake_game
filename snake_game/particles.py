# =============================================================================
# snake_game/particles.py — Particle burst system for food-eaten effects
# =============================================================================

import pygame
import random
import math
from snake_game.constants import PARTICLE_COUNT, PARTICLE_LIFETIME


class Particle:
    """One screen-space particle emitted on food-eat events."""

    __slots__ = ("x", "y", "vx", "vy", "color", "radius", "life", "max_life")

    def __init__(self, x: float, y: float, color: tuple):
        angle      = random.uniform(0, 2 * math.pi)
        speed      = random.uniform(1.5, 5.0)
        self.x, self.y = float(x), float(y)
        self.vx    = math.cos(angle) * speed
        self.vy    = math.sin(angle) * speed
        self.color = color
        self.radius   = random.randint(3, 7)
        self.max_life = PARTICLE_LIFETIME
        self.life     = self.max_life

    @property
    def alive(self) -> bool:
        return self.life > 0

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.vy += 0.12   # gentle gravity
        self.life -= 1

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        alpha  = int(255 * self.life / self.max_life)
        radius = max(1, int(self.radius * self.life / self.max_life))
        s = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (radius + 1, radius + 1), radius)
        surface.blit(s, (int(self.x) - radius - 1, int(self.y) - radius - 1))


class ParticleSystem:
    """Manages a live pool of particles."""

    def __init__(self):
        self._particles: list = []

    def spawn(self, px: int, py: int, color: tuple, count: int = PARTICLE_COUNT):
        for _ in range(count):
            self._particles.append(Particle(px, py, color))

    def update(self):
        self._particles = [p for p in self._particles if p.alive]
        for p in self._particles:
            p.update()

    def draw(self, surface: pygame.Surface):
        for p in self._particles:
            p.draw(surface)

    def clear(self):
        self._particles.clear()
