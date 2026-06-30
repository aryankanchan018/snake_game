# =============================================================================
# snake_game/game.py — Core Game class: state machine, loop, all gameplay logic
# =============================================================================

import pygame
import time
import struct
import math
from typing import Optional

from snake_game.constants import *
from snake_game.snake import Snake
from snake_game.food import Food, GoldenFood, PowerUp
from snake_game.particles import ParticleSystem
from snake_game.score_manager import ScoreManager
import snake_game.ui as ui


# ── Game States ───────────────────────────────────────────────────────────────

class State:
    MENU      = "menu"
    COUNTDOWN = "countdown"
    PLAYING   = "playing"
    PAUSED    = "paused"
    GAME_OVER = "game_over"
    STATS     = "stats"


class Game:
    """
    Top-level game object — call run() to start.

    Owns:
      - pygame window + clock
      - State machine (MENU → COUNTDOWN → PLAYING ↔ PAUSED → GAME_OVER)
      - All gameplay objects (Snake, Food, PowerUp, Particles)
      - ScoreManager for persistence
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock     = pygame.time.Clock()
        self.score_mgr = ScoreManager()
        self.particles = ParticleSystem()

        # Menu selections
        self._diff_options = list(DIFFICULTY_SPEEDS.keys())
        self._skin_options = list(SNAKE_SKINS.keys())
        self._diff_idx     = 1   # default: Medium
        self._skin_idx     = 0   # default: Classic

        self._sounds = _build_sounds()

        # Gameplay objects — populated in _start_game()
        self.snake:    Optional[Snake]     = None
        self.food:     Optional[Food]      = None
        self.golden:   Optional[GoldenFood] = None
        self.power_up: Optional[PowerUp]   = None

        # Runtime state
        self._score       = 0
        self._food_eaten  = 0
        self._combo       = 1
        self._last_eat_t  = 0.0
        self._active_pu:  Optional[str] = None
        self._pu_ticks    = 0
        self._base_mps    = DIFFICULTY_SPEEDS["Medium"]
        self._move_timer  = 0
        self._cd_start    = 0.0
        self._is_new_best = False

        self._state = State.MENU
        self._tick  = 0   # increments every frame for animations

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def _difficulty(self) -> str:
        return self._diff_options[self._diff_idx]

    @property
    def _skin(self) -> str:
        return self._skin_options[self._skin_idx]

    # ── Main Loop ─────────────────────────────────────────────────────────────

    def tick(self):
        """Advance one frame. Called by the async loop in main.py."""
        self._tick += 1
        self._handle_events()
        self._update()
        self._draw()
        self.clock.tick(FPS)

    def run(self):
        """Blocking loop for direct local execution (non-async fallback)."""
        while True:
            self.tick()

    # ── Input ─────────────────────────────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()
            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key: int):
        s = self._state

        # ESC is global
        if key == pygame.K_ESCAPE:
            if s in (State.PLAYING, State.PAUSED, State.COUNTDOWN, State.STATS):
                self._state = State.MENU
            else:
                # In browser (Pygbag) we can't quit — go back to menu instead
                self._state = State.MENU
            return

        if s == State.MENU:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()
            elif key == pygame.K_s:
                self._state = State.STATS
            elif key == pygame.K_LEFT:
                self._diff_idx = (self._diff_idx - 1) % len(self._diff_options)
            elif key == pygame.K_RIGHT:
                self._diff_idx = (self._diff_idx + 1) % len(self._diff_options)
            elif key == pygame.K_UP:
                self._skin_idx = (self._skin_idx - 1) % len(self._skin_options)
            elif key == pygame.K_DOWN:
                self._skin_idx = (self._skin_idx + 1) % len(self._skin_options)

        elif s == State.PLAYING:
            _DIR = {
                pygame.K_UP:    (0, -1),
                pygame.K_DOWN:  (0,  1),
                pygame.K_LEFT:  (-1, 0),
                pygame.K_RIGHT: (1,  0),
            }
            if key in _DIR:
                self.snake.set_direction(*_DIR[key])
            elif key == pygame.K_p:
                self._state = State.PAUSED
            elif key == pygame.K_r:
                self._start_game()

        elif s == State.PAUSED:
            if key == pygame.K_p:
                self._state = State.PLAYING
            elif key == pygame.K_r:
                self._start_game()

        elif s == State.GAME_OVER:
            if key == pygame.K_r:
                self._start_game()
            elif key == pygame.K_m:
                self._state = State.MENU

    # ── Game Initialisation ───────────────────────────────────────────────────

    def _start_game(self):
        """Reset all objects and start the countdown."""
        self.snake    = Snake(self._skin)
        self.food     = Food(self.snake.body)
        self.golden   = None
        self.power_up = None
        self.particles.clear()

        self._score      = 0
        self._food_eaten = 0
        self._combo      = 1
        self._last_eat_t = 0.0

        self._active_pu  = None
        self._pu_ticks   = 0
        self._base_mps   = DIFFICULTY_SPEEDS[self._difficulty]
        self._move_timer = 0
        self._is_new_best = False

        self._cd_start = time.time()
        self._state    = State.COUNTDOWN

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self):
        if self._state == State.COUNTDOWN:
            self._update_countdown()
        elif self._state == State.PLAYING:
            self._update_game()
        # Particles keep animating during pause / game-over
        self.particles.update()

    def _update_countdown(self):
        elapsed = time.time() - self._cd_start
        # COUNTDOWN_SECS seconds of numbers + 0.6 s showing "GO!"
        if elapsed >= COUNTDOWN_SECS + 0.6:
            self._state = State.PLAYING

    def _update_game(self):
        # ── Determine current speed ───────────────────────────────────────
        level_bonus = min(self._score // (BASE_SCORE * SPEED_UP_EVERY), MAX_MPS)
        mps = self._base_mps + level_bonus

        if self._active_pu == "speed":
            mps = min(mps * 2, MAX_MPS)
        elif self._active_pu == "slow":
            mps = max(mps // 2, 2)

        frames_per_move = max(1, FPS // mps)

        # ── Tick the move timer ───────────────────────────────────────────
        self._move_timer += 1
        if self._move_timer < frames_per_move:
            return
        self._move_timer = 0

        # ── Decrement power-up timer ──────────────────────────────────────
        if self._active_pu:
            self._pu_ticks -= 1
            if self._pu_ticks <= 0:
                self._active_pu = None
                self._pu_ticks  = 0

        # ── Move snake ────────────────────────────────────────────────────
        if not self.snake.move():
            self._end_game()
            return

        head = self.snake.head

        # ── Normal food ───────────────────────────────────────────────────
        if head == self.food.pos:
            self._eat_food(self.food, golden=False)
            self._food_eaten += 1
            self.food.respawn(self._all_occupied())
            self._maybe_spawn_golden()
            self._maybe_spawn_powerup()

        # ── Golden food ───────────────────────────────────────────────────
        if self.golden and head == self.golden.pos:
            self._eat_food(self.golden, golden=True)
            self._food_eaten += 1
            self.golden = None

        # ── Power-up ──────────────────────────────────────────────────────
        if self.power_up and head == self.power_up.pos:
            self._collect_powerup(self.power_up)
            self.power_up = None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _all_occupied(self):
        """Return all grid positions currently blocked."""
        occupied = list(self.snake.body)
        if self.golden:
            occupied.append(self.golden.pos)
        if self.power_up:
            occupied.append(self.power_up.pos)
        return occupied

    def _eat_food(self, food_obj, golden: bool):
        now = time.time()
        if now - self._last_eat_t > COMBO_WINDOW:
            self._combo = 1
        else:
            self._combo += 1
        self._last_eat_t = now

        base   = GOLDEN_SCORE if golden else BASE_SCORE
        mult   = 2 if self._active_pu == "double" else 1
        points = int(base * mult * (1 + (self._combo - 1) * COMBO_MULTIPLIER))
        self._score += points

        self.snake.grow(1)

        col, row = food_obj.pos
        px = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        py = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        color = GOLDEN_COLOR if golden else FOOD_COLOR
        self.particles.spawn(px, py, color, PARTICLE_COUNT + self._combo * 2)
        self._play("eat")

    def _collect_powerup(self, pu: PowerUp):
        self._active_pu = pu.kind
        self._pu_ticks  = PU_DURATION
        self._play("powerup")

    def _maybe_spawn_golden(self):
        if self._food_eaten % GOLDEN_EVERY == 0:
            self.golden = GoldenFood(self._all_occupied() + [self.food.pos])

    def _maybe_spawn_powerup(self):
        if self._food_eaten % PU_SPAWN_EVERY == 0 and not self.power_up:
            self.power_up = PowerUp(self._all_occupied() + [self.food.pos])

    def _end_game(self):
        self._is_new_best = self._score > self.score_mgr.high_score
        self.score_mgr.record_game(self._score, self._food_eaten, self.snake.length)
        self._play("die")
        self._state = State.GAME_OVER

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _draw(self):
        s = self._state

        if s == State.MENU:
            ui.draw_main_menu(self.screen, self._tick,
                              self._difficulty, self._skin,
                              self.score_mgr.high_score)

        elif s == State.STATS:
            ui.draw_stats_screen(self.screen, self.score_mgr)

        else:
            # All in-game states share the gameplay scene underneath
            self._draw_gameplay()

            if s == State.COUNTDOWN:
                elapsed   = time.time() - self._cd_start
                remaining = COUNTDOWN_SECS - int(elapsed)
                ui.draw_countdown(self.screen, max(remaining, 0))
            elif s == State.PAUSED:
                ui.draw_pause(self.screen)
            elif s == State.GAME_OVER:
                ui.draw_game_over(self.screen, self._score,
                                  self.score_mgr.high_score,
                                  self._is_new_best)

        pygame.display.flip()

    def _draw_gameplay(self):
        ui.draw_background(self.screen)
        ui.draw_grid(self.screen)
        ui.draw_play_border(self.screen)

        self.food.draw(self.screen, self._tick)
        if self.golden:
            self.golden.draw(self.screen, self._tick)
        if self.power_up:
            self.power_up.draw(self.screen, self._tick)

        self.snake.draw(self.screen, self._tick)
        self.particles.draw(self.screen)

        ui.draw_hud(
            self.screen,
            score      = self._score,
            high_score = self.score_mgr.high_score,
            active_pu  = self._active_pu,
            pu_ticks   = self._pu_ticks,
            combo      = self._combo,
            difficulty = self._difficulty,
        )

    # ── Sound ─────────────────────────────────────────────────────────────────

    def _play(self, name: str):
        sound = self._sounds.get(name)
        if sound:
            sound.play()


# ── Utilities ─────────────────────────────────────────────────────────────────

def _quit():
    pygame.quit()
    raise SystemExit


def _build_sounds() -> dict:
    """
    Procedurally synthesise all sound effects as PCM byte buffers.
    No external audio files required.
    """
    rate = 44100

    def sine_wave(freq: float, duration: float, volume: float = 0.4) -> pygame.mixer.Sound:
        n = int(rate * duration)
        buf = bytearray(n * 2)
        for i in range(n):
            t   = i / rate
            env = 1 - t / duration
            val = max(-32768, min(32767, int(volume * env * 32767 * math.sin(2 * math.pi * freq * t))))
            struct.pack_into("<h", buf, i * 2, val)
        s = pygame.mixer.Sound(buffer=bytes(buf))
        s.set_volume(volume)
        return s

    def chord(freqs: list, duration: float, volume: float = 0.35) -> pygame.mixer.Sound:
        n       = int(rate * duration)
        samples = [0.0] * n
        for freq in freqs:
            for i in range(n):
                t = i / rate
                samples[i] += (volume / len(freqs)) * (1 - t / duration) * math.sin(2 * math.pi * freq * t)
        buf = bytearray(n * 2)
        for i, s in enumerate(samples):
            struct.pack_into("<h", buf, i * 2, max(-32768, min(32767, int(s * 32767))))
        snd = pygame.mixer.Sound(buffer=bytes(buf))
        snd.set_volume(volume)
        return snd

    sounds = {}
    try:
        sounds["eat"]     = sine_wave(880, 0.08, 0.35)
        sounds["powerup"] = chord([523, 659, 784], 0.35, 0.4)
        sounds["die"]     = chord([200, 160, 120], 0.65, 0.5)
    except Exception:
        pass  # Mixer unavailable — game runs silently
    return sounds
