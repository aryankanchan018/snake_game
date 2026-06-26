# =============================================================================
# game.py — Core Game class: state machine, update loop, collision, scoring
# =============================================================================

import pygame
import time
import math
from constants import *
from snake import Snake
from food import Food, GoldenFood, PowerUp
from particles import ParticleSystem
from score_manager import ScoreManager
import ui


# ── Game States ───────────────────────────────────────────────────────────────

class State:
    MENU       = "menu"
    COUNTDOWN  = "countdown"
    PLAYING    = "playing"
    PAUSED     = "paused"
    GAME_OVER  = "game_over"
    STATS      = "stats"


class Game:
    """
    Top-level game object.  Call `run()` to start the main loop.

    Responsibilities:
      - Window & clock management
      - State machine (Menu → Countdown → Playing → Paused / GameOver)
      - Input routing
      - Delegating to Snake, Food, PowerUp, ParticleSystem, ScoreManager, UI
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.screen  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock      = pygame.time.Clock()
        self.score_mgr  = ScoreManager()
        self.particles  = ParticleSystem()

        # Menu selection state
        self._diff_options  = list(DIFFICULTY_SPEEDS.keys())
        self._skin_options  = list(SNAKE_SKINS.keys())
        self._diff_idx      = 1   # Default: Medium
        self._skin_idx      = 0

        # Sound assets
        self._sounds = _build_sounds()

        # Will be populated in _start_game()
        self.snake: Snake         = None
        self.food:  Food          = None
        self.golden: GoldenFood   = None
        self.power_up: PowerUp    = None

        self._state = State.MENU
        self._tick  = 0            # global animation tick (every frame)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def _difficulty(self) -> str:
        return self._diff_options[self._diff_idx]

    @property
    def _skin(self) -> str:
        return self._skin_options[self._skin_idx]

    # ── Public Entry Point ────────────────────────────────────────────────────

    def run(self):
        while True:
            self._tick += 1
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    # ── Event Handling ────────────────────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key: int):
        s = self._state

        # ── Global ────────────────────────────────────────────────────────────
        if key == pygame.K_ESCAPE:
            if s in (State.PLAYING, State.PAUSED, State.COUNTDOWN):
                self._state = State.MENU
            elif s == State.STATS:
                self._state = State.MENU
            else:
                self._quit()
            return

        # ── Menu ──────────────────────────────────────────────────────────────
        if s == State.MENU:
            diffs = self._diff_options
            skins = self._skin_options

            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()
            elif key == pygame.K_s:
                self._state = State.STATS
            elif key == pygame.K_LEFT:
                self._diff_idx = (self._diff_idx - 1) % len(diffs)
            elif key == pygame.K_RIGHT:
                self._diff_idx = (self._diff_idx + 1) % len(diffs)
            elif key == pygame.K_UP:
                self._skin_idx = (self._skin_idx - 1) % len(skins)
            elif key == pygame.K_DOWN:
                self._skin_idx = (self._skin_idx + 1) % len(skins)

        # ── Stats ─────────────────────────────────────────────────────────────
        elif s == State.STATS:
            if key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                self._state = State.MENU

        # ── Playing ───────────────────────────────────────────────────────────
        elif s == State.PLAYING:
            DIR_KEYS = {
                pygame.K_UP:    (0, -1),
                pygame.K_DOWN:  (0,  1),
                pygame.K_LEFT:  (-1, 0),
                pygame.K_RIGHT: (1,  0),
            }
            if key in DIR_KEYS:
                self.snake.set_direction(*DIR_KEYS[key])
            elif key == pygame.K_p:
                self._state = State.PAUSED
            elif key == pygame.K_r:
                self._start_game()

        # ── Paused ────────────────────────────────────────────────────────────
        elif s == State.PAUSED:
            if key == pygame.K_p:
                self._state = State.PLAYING
            elif key == pygame.K_r:
                self._start_game()

        # ── Game Over ─────────────────────────────────────────────────────────
        elif s == State.GAME_OVER:
            if key == pygame.K_r:
                self._start_game()

    # ── Game Initialisation ───────────────────────────────────────────────────

    def _start_game(self):
        """Reset all gameplay objects and enter the countdown."""
        self.snake     = Snake(self._skin)
        self.food      = Food(self.snake.body)
        self.golden    = None
        self.power_up  = None
        self.particles.clear()

        self._score       = 0
        self._food_eaten  = 0
        self._combo       = 1
        self._last_eat_t  = 0.0

        self._active_pu   = None    # current power-up type
        self._pu_ticks    = 0       # remaining ticks

        self._base_mps    = DIFFICULTY_SPEEDS[self._difficulty]
        self._move_timer  = 0       # frame counter between snake moves

        self._is_new_best = False

        # Countdown
        self._cd_start    = time.time()
        self._state       = State.COUNTDOWN

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self):
        s = self._state

        if s == State.COUNTDOWN:
            self._update_countdown()

        elif s == State.PLAYING:
            self._update_game()

        # Particles animate in paused / game-over too for visual polish
        self.particles.update()

    def _update_countdown(self):
        elapsed = time.time() - self._cd_start
        if elapsed >= COUNTDOWN_SECS + 0.5:   # +0.5 for "GO!" display
            self._state = State.PLAYING

    def _update_game(self):
        # ── Speed calculation ──────────────────────────────────────────────
        speed_boost = self._active_pu == "speed"
        slow_motion = self._active_pu == "slow"

        # Increase base mps every SPEED_UP_EVERY points
        level_bonus = min(self._score // (BASE_SCORE * SPEED_UP_EVERY), MAX_MPS)
        mps = self._base_mps + level_bonus

        if speed_boost:
            mps = min(mps * 2, MAX_MPS)
        elif slow_motion:
            mps = max(mps // 2, 2)

        frames_per_move = max(1, FPS // mps)

        # ── Advance snake on correct frame ────────────────────────────────
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
        alive = self.snake.move()
        if not alive:
            self._end_game()
            return

        head = self.snake.head

        # ── Food collision ────────────────────────────────────────────────
        if head == self.food.pos:
            self._eat_food(self.food, golden=False)
            self.food.respawn(self.snake.body)
            self._food_eaten += 1
            self._maybe_spawn_golden()
            self._maybe_spawn_powerup()

        # ── Golden food collision ─────────────────────────────────────────
        if self.golden and head == self.golden.pos:
            self._eat_food(self.golden, golden=True)
            self.golden = None

        # ── Power-up collision ────────────────────────────────────────────
        if self.power_up and head == self.power_up.pos:
            self._collect_powerup(self.power_up)
            self.power_up = None

    # ── Eating & Scoring ──────────────────────────────────────────────────────

    def _eat_food(self, food_obj, golden: bool):
        now = time.time()
        # Combo: reset if too long since last eat
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

        # Particles burst at food pixel centre
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

    # ── Spawning Logic ────────────────────────────────────────────────────────

    def _maybe_spawn_golden(self):
        if self._food_eaten % GOLDEN_EVERY == 0:
            self.golden = GoldenFood(self.snake.body + [self.food.pos])

    def _maybe_spawn_powerup(self):
        if self._food_eaten % PU_SPAWN_EVERY == 0 and not self.power_up:
            occupied = self.snake.body + [self.food.pos]
            if self.golden:
                occupied.append(self.golden.pos)
            self.power_up = PowerUp(occupied)

    # ── End of Game ───────────────────────────────────────────────────────────

    def _end_game(self):
        prev_best         = self.score_mgr.high_score
        self._is_new_best = self._score > prev_best
        self.score_mgr.record_game(
            self._score, self._food_eaten, self.snake.length
        )
        self._play("die")
        self._state = State.GAME_OVER

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        s = self._state

        if s == State.MENU:
            ui.draw_main_menu(self.screen, self._tick,
                              self._difficulty, self._skin,
                              self.score_mgr.high_score)

        elif s == State.STATS:
            ui.draw_stats_screen(self.screen, self.score_mgr)

        elif s in (State.COUNTDOWN, State.PLAYING,
                   State.PAUSED, State.GAME_OVER):
            self._draw_gameplay()

            if s == State.COUNTDOWN:
                elapsed = time.time() - self._cd_start
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
        """Render the in-game scene: background, grid, entities, HUD."""
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

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _play(self, name: str):
        sound = self._sounds.get(name)
        if sound:
            sound.play()

    @staticmethod
    def _quit():
        pygame.quit()
        raise SystemExit


# ── Sound Generation ──────────────────────────────────────────────────────────

def _build_sounds() -> dict[str, pygame.mixer.Sound]:
    """
    Generate simple synthesised sounds procedurally — no audio files needed.
    Each sound is a short numpy-free sine wave written into a bytes buffer.
    """
    import struct, math as _math

    rate = 44100

    def sine_wave(freq: float, duration: float, volume: float = 0.4,
                  decay: bool = True) -> pygame.mixer.Sound:
        n_samples = int(rate * duration)
        buf = bytearray(n_samples * 2)  # 16-bit mono
        for i in range(n_samples):
            t     = i / rate
            env   = (1 - t / duration) if decay else 1.0
            val   = int(volume * env * 32767 * _math.sin(2 * _math.pi * freq * t))
            val   = max(-32768, min(32767, val))
            struct.pack_into("<h", buf, i * 2, val)
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound

    def chord(freqs, duration, volume=0.3):
        """Mix multiple sine waves into one sound."""
        n_samples = int(rate * duration)
        samples   = [0.0] * n_samples
        for freq in freqs:
            for i in range(n_samples):
                t = i / rate
                env = 1 - t / duration
                samples[i] += volume / len(freqs) * env * _math.sin(2 * _math.pi * freq * t)
        buf = bytearray(n_samples * 2)
        for i, s in enumerate(samples):
            val = max(-32768, min(32767, int(s * 32767)))
            struct.pack_into("<h", buf, i * 2, val)
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound

    sounds = {}
    try:
        sounds["eat"]     = sine_wave(880, 0.08, 0.35)
        sounds["powerup"] = chord([523, 659, 784], 0.35, 0.4)
        sounds["die"]     = chord([200, 160, 120], 0.6, 0.5)
    except Exception:
        pass  # If mixer fails, game still works — just silent
    return sounds
