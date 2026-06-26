# =============================================================================
# snake_game/ui.py — All UI drawing: menus, HUD, overlays, screens
# =============================================================================

import pygame
import math
from snake_game.constants import *

# ── Font cache ────────────────────────────────────────────────────────────────

_font_cache: dict = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("consolas", size, bold=bold)
    return _font_cache[key]


# ── Background (cached surface — drawn once, blitted every frame) ─────────────

_bg_cache: pygame.Surface = None

def draw_background(surface: pygame.Surface):
    """Blit a pre-rendered gradient background — O(1) after first call."""
    global _bg_cache
    if _bg_cache is None:
        _bg_cache = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            color = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
            pygame.draw.line(_bg_cache, color, (0, y), (WINDOW_WIDTH, y))
    surface.blit(_bg_cache, (0, 0))


def draw_grid(surface: pygame.Surface):
    """Subtle grid lines inside the play area."""
    for col in range(GRID_COLS + 1):
        x = GRID_OFFSET_X + col * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (x, GRID_OFFSET_Y), (x, GRID_OFFSET_Y + PLAY_H))
    for row in range(GRID_ROWS + 1):
        y = GRID_OFFSET_Y + row * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (GRID_OFFSET_X, y), (GRID_OFFSET_X + PLAY_W, y))


def draw_play_border(surface: pygame.Surface):
    """Glowing border around the play area."""
    rect = pygame.Rect(GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2, PLAY_W + 4, PLAY_H + 4)
    pygame.draw.rect(surface, BORDER_COLOR, rect, 2, border_radius=4)


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surface: pygame.Surface, score: int, high_score: int,
             active_pu, pu_ticks: int, combo: int, difficulty: str):
    """Top HUD: score, best, difficulty, combo, power-up bar."""
    pygame.draw.rect(surface, HUD_BG, (0, 0, WINDOW_WIDTH, GRID_OFFSET_Y - 4))
    pygame.draw.line(surface, BORDER_COLOR,
                     (0, GRID_OFFSET_Y - 4), (WINDOW_WIDTH, GRID_OFFSET_Y - 4), 1)

    _blit(surface, TITLE,                  get_font(22, True), COLOR_TITLE,
          (WINDOW_WIDTH // 2, 20), center=True)
    _blit(surface, f"SCORE  {score:06d}",  get_font(16, True), COLOR_WHITE,
          (GRID_OFFSET_X + 10, 48))
    _blit(surface, f"BEST  {high_score:06d}", get_font(16, True), COLOR_YELLOW,
          (GRID_OFFSET_X + 200, 48))
    _blit(surface, difficulty.upper(),     get_font(13), LIGHT_GRAY,
          (GRID_OFFSET_X + 395, 50))

    if combo >= 2:
        color = COLOR_ORANGE if combo < 5 else COLOR_RED
        _blit(surface, f"COMBO x{combo}", get_font(16, True), color,
              (WINDOW_WIDTH - 260, 48))

    if active_pu:
        _draw_pu_bar(surface, active_pu, pu_ticks)


def _draw_pu_bar(surface: pygame.Surface, kind: str, ticks: int):
    colors = {"speed": PU_SPEED_COLOR, "slow": PU_SLOW_COLOR, "double": PU_DOUBLE_COLOR}
    labels = {"speed": "SPD BOOST", "slow": "SLO-MO", "double": "x2 SCORE"}
    color  = colors[kind]
    bar_w  = int(180 * (ticks / PU_DURATION))
    pygame.draw.rect(surface, GRAY,  (WINDOW_WIDTH - 210, 12, 180, 14), border_radius=7)
    pygame.draw.rect(surface, color, (WINDOW_WIDTH - 210, 12, bar_w,  14), border_radius=7)
    _blit(surface, labels[kind], get_font(12, True), WHITE,
          (WINDOW_WIDTH - 120, 14), center=True)


# ── Countdown ─────────────────────────────────────────────────────────────────

def draw_countdown(surface: pygame.Surface, value: int):
    _overlay(surface, 160)
    label = str(value) if value > 0 else "GO!"
    color = COLOR_YELLOW if value > 0 else COLOR_GREEN
    _blit(surface, label, get_font(120, True), color,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), center=True)


# ── Pause ─────────────────────────────────────────────────────────────────────

def draw_pause(surface: pygame.Surface):
    _overlay(surface, 170)
    _blit(surface, "PAUSED", get_font(72, True), COLOR_CYAN,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40), center=True)
    _blit(surface, "P — Resume    R — Restart    ESC — Quit",
          get_font(16), LIGHT_GRAY,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50), center=True)


# ── Game Over ─────────────────────────────────────────────────────────────────

def draw_game_over(surface: pygame.Surface, score: int,
                   high_score: int, is_new_best: bool):
    _overlay(surface, 185)
    _blit(surface, "GAME OVER", get_font(72, True), COLOR_RED,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 110), center=True)

    score_color = COLOR_YELLOW if is_new_best else COLOR_WHITE
    _blit(surface, f"Score: {score}", get_font(30, True), score_color,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 25), center=True)

    if is_new_best:
        _blit(surface, "NEW HIGH SCORE!", get_font(22, True), COLOR_YELLOW,
              (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20), center=True)

    _blit(surface, "R — Restart         ESC — Main Menu",
          get_font(18), LIGHT_GRAY,
          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 68), center=True)


# ── Main Menu ─────────────────────────────────────────────────────────────────

def draw_main_menu(surface: pygame.Surface, tick: int,
                   selected_diff: str, selected_skin: str, high_score: int):
    draw_background(surface)
    _draw_title_snake(surface, tick)

    # Title with subtle wave
    wy = int(4 * math.sin(tick * 0.05))
    _blit(surface, "SNAKE  GAME", get_font(62, True), COLOR_TITLE,
          (WINDOW_WIDTH // 2, 108 + wy), center=True)
    _blit(surface, "A modern Pygame adventure", get_font(16), COLOR_SUBTITLE,
          (WINDOW_WIDTH // 2, 175), center=True)
    _blit(surface, f"BEST SCORE:  {high_score}", get_font(18, True), COLOR_YELLOW,
          (WINDOW_WIDTH // 2, 212), center=True)

    # Difficulty row — changed with LEFT / RIGHT
    _blit(surface, "DIFFICULTY   ( LEFT / RIGHT )", get_font(14, True), LIGHT_GRAY,
          (WINDOW_WIDTH // 2, 262), center=True)
    diffs = list(DIFFICULTY_SPEEDS.keys())
    _draw_selector(surface, diffs, selected_diff,
                   WINDOW_WIDTH // 2 - 180, 283, 120,
                   {d: c for d, c in zip(diffs, [COLOR_GREEN, COLOR_ORANGE, COLOR_RED])})

    # Skin row — changed with UP / DOWN
    _blit(surface, "SNAKE SKIN   ( UP / DOWN )", get_font(14, True), LIGHT_GRAY,
          (WINDOW_WIDTH // 2, 350), center=True)
    skins = list(SNAKE_SKINS.keys())
    _draw_selector(surface, skins, selected_skin,
                   WINDOW_WIDTH // 2 - 220, 372, 110,
                   {s: SNAKE_SKINS[s][2] for s in skins})

    _blit(surface, "ENTER / SPACE — Start Game",
          get_font(16, True), COLOR_GREEN,
          (WINDOW_WIDTH // 2, 448), center=True)
    _blit(surface, "S — Statistics          ESC — Quit",
          get_font(13), GRAY,
          (WINDOW_WIDTH // 2, 476), center=True)

    # Controls legend bar
    pygame.draw.line(surface, GRID_COLOR, (60, 515), (WINDOW_WIDTH - 60, 515))
    for i, item in enumerate(["Arrow Keys  Move", "P  Pause", "R  Restart", "ESC  Quit"]):
        _blit(surface, item, get_font(13), LIGHT_GRAY, (130 + i * 168, 528))


# ── Statistics Screen ─────────────────────────────────────────────────────────

def draw_stats_screen(surface: pygame.Surface, sm):
    draw_background(surface)
    _blit(surface, "STATISTICS", get_font(50, True), COLOR_TITLE,
          (WINDOW_WIDTH // 2, 80), center=True)

    rows = [
        ("Highest Score",    str(sm.high_score),    COLOR_YELLOW),
        ("Games Played",     str(sm.games_played),  COLOR_WHITE),
        ("Total Food Eaten", str(sm.total_food),     COLOR_GREEN),
        ("Longest Snake",    str(sm.longest_snake),  COLOR_CYAN),
    ]
    for i, (label, value, color) in enumerate(rows):
        y   = 195 + i * 72
        box = pygame.Rect(WINDOW_WIDTH // 2 - 230, y - 10, 460, 52)
        pygame.draw.rect(surface, HUD_BG,       box, border_radius=8)
        pygame.draw.rect(surface, BORDER_COLOR, box, 1, border_radius=8)
        _blit(surface, label, get_font(18), LIGHT_GRAY,  (box.x + 20, y + 7))
        _blit(surface, value, get_font(22, True), color, (box.right - 20, y + 5), right=True)

    _blit(surface, "ESC — Back to Menu", get_font(15), LIGHT_GRAY,
          (WINDOW_WIDTH // 2, 520), center=True)


# ── Private helpers ───────────────────────────────────────────────────────────

def _overlay(surface: pygame.Surface, alpha: int):
    s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surface.blit(s, (0, 0))


def _blit(surface, text, font, color, pos, center=False, right=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=pos)
    elif right:
        rect = img.get_rect(topright=pos)
    else:
        rect = img.get_rect(topleft=pos)
    surface.blit(img, rect)


def _draw_selector(surface, options, selected, start_x, y, spacing, color_map):
    for i, opt in enumerate(options):
        x      = start_x + i * spacing
        is_sel = (opt == selected)
        color  = color_map.get(opt, COLOR_WHITE)
        box    = pygame.Rect(x, y, spacing - 8, 36)
        pygame.draw.rect(surface, color if is_sel else HUD_BG, box, border_radius=10)
        pygame.draw.rect(surface, color, box, 2, border_radius=10)
        _blit(surface, opt, get_font(14, True), BLACK if is_sel else color,
              box.center, center=True)


def _draw_title_snake(surface: pygame.Surface, tick: int):
    """Animated sine-wave snake decoration across the top of the menu."""
    for i in range(60):
        x = 30 + i * 14
        y = 50 + int(14 * math.sin(i * 0.4 + tick * 0.06))
        t = i / 59
        color = (int(50 * (1 - t)), int(180 + 40 * t), int(80 + 60 * t))
        pygame.draw.circle(surface, color, (x, y), 5)
