# =============================================================================
# ui.py — All UI drawing helpers: menus, HUD, overlays, screens
# =============================================================================

import pygame
import math
from constants import *


# ── Font Cache ────────────────────────────────────────────────────────────────

_font_cache: dict[tuple, pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a cached SysFont('consolas') instance."""
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("consolas", size, bold=bold)
    return _font_cache[key]


# ── Background ────────────────────────────────────────────────────────────────

def draw_background(surface: pygame.Surface):
    """Vertical gradient background."""
    for y in range(WINDOW_HEIGHT):
        t = y / WINDOW_HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))


def draw_grid(surface: pygame.Surface):
    """Subtle grid lines inside the play area."""
    for col in range(GRID_COLS + 1):
        x = GRID_OFFSET_X + col * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR,
                         (x, GRID_OFFSET_Y), (x, GRID_OFFSET_Y + PLAY_H))
    for row in range(GRID_ROWS + 1):
        y = GRID_OFFSET_Y + row * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR,
                         (GRID_OFFSET_X, y), (GRID_OFFSET_X + PLAY_W, y))


def draw_play_border(surface: pygame.Surface):
    """Glowing border around the play area."""
    rect = pygame.Rect(GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2,
                       PLAY_W + 4, PLAY_H + 4)
    pygame.draw.rect(surface, BORDER_COLOR, rect, 2, border_radius=4)


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surface: pygame.Surface, score: int, high_score: int,
             active_pu: str | None, pu_ticks: int, combo: int, difficulty: str):
    """Top HUD bar showing score, high score, power-up status, and combo."""
    # Background bar
    bar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, GRID_OFFSET_Y - 4)
    pygame.draw.rect(surface, HUD_BG, bar_rect)
    pygame.draw.line(surface, BORDER_COLOR,
                     (0, GRID_OFFSET_Y - 4), (WINDOW_WIDTH, GRID_OFFSET_Y - 4), 1)

    # Title
    _blit_text(surface, TITLE, get_font(22, True), COLOR_TITLE,
               (WINDOW_WIDTH // 2, 20), center=True)

    # Score
    _blit_text(surface, f"SCORE  {score:06d}", get_font(16, True), COLOR_WHITE,
               (GRID_OFFSET_X + 10, 48))

    # High score
    _blit_text(surface, f"BEST  {high_score:06d}", get_font(16, True), COLOR_YELLOW,
               (GRID_OFFSET_X + 200, 48))

    # Difficulty
    _blit_text(surface, difficulty.upper(), get_font(13), LIGHT_GRAY,
               (GRID_OFFSET_X + 390, 50))

    # Combo
    if combo >= 2:
        color  = COLOR_ORANGE if combo < 5 else COLOR_RED
        _blit_text(surface, f"COMBO ×{combo}", get_font(16, True), color,
                   (WINDOW_WIDTH - 260, 48))

    # Active power-up timer bar
    if active_pu:
        pu_colors = {"speed": PU_SPEED_COLOR, "slow": PU_SLOW_COLOR,
                     "double": PU_DOUBLE_COLOR}
        labels = {"speed": "⚡ SPEED", "slow": "❄ SLOW", "double": "×2 DOUBLE"}
        bar_w  = int(180 * (pu_ticks / PU_DURATION))
        pygame.draw.rect(surface, GRAY,         (WINDOW_WIDTH - 210, 12, 180, 14), border_radius=7)
        pygame.draw.rect(surface, pu_colors[active_pu], (WINDOW_WIDTH - 210, 12, bar_w, 14), border_radius=7)
        _blit_text(surface, labels[active_pu], get_font(12, True), WHITE,
                   (WINDOW_WIDTH - 120, 14), center=True)


# ── Countdown ─────────────────────────────────────────────────────────────────

def draw_countdown(surface: pygame.Surface, value: int):
    """Full-screen semi-transparent countdown overlay."""
    _draw_overlay(surface, 160)
    label = str(value) if value > 0 else "GO!"
    color = COLOR_YELLOW if value > 0 else COLOR_GREEN
    _blit_text(surface, label, get_font(120, True), color,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), center=True)


# ── Pause Screen ──────────────────────────────────────────────────────────────

def draw_pause(surface: pygame.Surface):
    _draw_overlay(surface, 170)
    _blit_text(surface, "PAUSED", get_font(72, True), COLOR_CYAN,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40), center=True)
    _blit_text(surface, "Press  P  to Resume  |  R  to Restart  |  ESC  to Quit",
               get_font(16), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50), center=True)


# ── Game Over Screen ──────────────────────────────────────────────────────────

def draw_game_over(surface: pygame.Surface, score: int, high_score: int,
                   is_new_best: bool):
    _draw_overlay(surface, 180)
    _blit_text(surface, "GAME OVER", get_font(72, True), COLOR_RED,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100), center=True)

    score_color = COLOR_YELLOW if is_new_best else COLOR_WHITE
    _blit_text(surface, f"Score: {score}", get_font(28, True), score_color,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20), center=True)

    if is_new_best:
        _blit_text(surface, "✦ NEW HIGH SCORE! ✦", get_font(20, True), COLOR_YELLOW,
                   (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 18), center=True)

    _blit_text(surface, "R — Restart    ESC — Quit", get_font(18), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60), center=True)


# ── Main Menu ─────────────────────────────────────────────────────────────────

def draw_main_menu(surface: pygame.Surface, tick: int,
                   selected_diff: str, selected_skin: str, high_score: int):
    """Animated title screen with difficulty and skin selection."""
    draw_background(surface)

    # Animated snake title decoration
    _draw_title_snake(surface, tick)

    # Title
    wave_y = int(4 * math.sin(tick * 0.05))
    _blit_text(surface, "🐍  SNAKE  GAME", get_font(58, True), COLOR_TITLE,
               (WINDOW_WIDTH // 2, 110 + wave_y), center=True)
    _blit_text(surface, "A modern Pygame adventure", get_font(16), COLOR_SUBTITLE,
               (WINDOW_WIDTH // 2, 175), center=True)

    # High score
    _blit_text(surface, f"BEST SCORE:  {high_score}", get_font(18, True), COLOR_YELLOW,
               (WINDOW_WIDTH // 2, 215), center=True)

    # Difficulty selector
    _blit_text(surface, "DIFFICULTY", get_font(16, True), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, 268), center=True)
    diffs = list(DIFFICULTY_SPEEDS.keys())
    _draw_selector(surface, diffs, selected_diff,
                   WINDOW_WIDTH // 2 - 180, 290, 120,
                   {d: (COLOR_GREEN, COLOR_ORANGE, COLOR_RED)[i]
                    for i, d in enumerate(diffs)})

    # Skin selector
    _blit_text(surface, "SNAKE SKIN", get_font(16, True), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, 360), center=True)
    skins = list(SNAKE_SKINS.keys())
    _draw_selector(surface, skins, selected_skin,
                   WINDOW_WIDTH // 2 - 220, 382, 110,
                   {s: SNAKE_SKINS[s][2] for s in skins})

    # Controls hint
    _blit_text(surface, "← / → CHANGE SELECTION      ENTER / SPACE — START",
               get_font(14), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, 460), center=True)
    _blit_text(surface, "ESC — Quit      S — Statistics",
               get_font(13), GRAY,
               (WINDOW_WIDTH // 2, 485), center=True)

    # Controls legend
    legend_y = 525
    pygame.draw.line(surface, GRID_COLOR, (60, legend_y), (WINDOW_WIDTH - 60, legend_y))
    items = ["↑↓←→  Move", "P  Pause", "R  Restart", "ESC  Quit"]
    for i, item in enumerate(items):
        _blit_text(surface, item, get_font(13), LIGHT_GRAY,
                   (160 + i * 160, legend_y + 20))


def draw_stats_screen(surface: pygame.Surface, sm):
    """Full statistics overlay."""
    draw_background(surface)
    _blit_text(surface, "STATISTICS", get_font(48, True), COLOR_TITLE,
               (WINDOW_WIDTH // 2, 80), center=True)

    rows = [
        ("Highest Score",    str(sm.high_score),    COLOR_YELLOW),
        ("Games Played",     str(sm.games_played),  COLOR_WHITE),
        ("Total Food Eaten", str(sm.total_food),     COLOR_GREEN),
        ("Longest Snake",    str(sm.longest_snake),  COLOR_CYAN),
    ]
    for i, (label, value, color) in enumerate(rows):
        y = 200 + i * 70
        box = pygame.Rect(WINDOW_WIDTH // 2 - 220, y - 10, 440, 50)
        pygame.draw.rect(surface, HUD_BG, box, border_radius=8)
        pygame.draw.rect(surface, BORDER_COLOR, box, 1, border_radius=8)
        _blit_text(surface, label, get_font(18), LIGHT_GRAY, (box.x + 20, y + 6))
        _blit_text(surface, value, get_font(22, True), color,
                   (box.right - 20, y + 4), right=True)

    _blit_text(surface, "Press  BACKSPACE  or  ESC  to go back",
               get_font(15), LIGHT_GRAY,
               (WINDOW_WIDTH // 2, 520), center=True)


# ── Private Helpers ───────────────────────────────────────────────────────────

def _draw_overlay(surface: pygame.Surface, alpha: int):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))


def _blit_text(surface, text, font, color, pos, center=False, right=False):
    rendered = font.render(text, True, color)
    if center:
        rect = rendered.get_rect(center=pos)
    elif right:
        rect = rendered.get_rect(topright=pos)
    else:
        rect = rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)


def _draw_selector(surface, options, selected, start_x, y, spacing, color_map):
    """Row of pill buttons; highlighted one is selected."""
    for i, opt in enumerate(options):
        x = start_x + i * spacing
        is_sel = (opt == selected)
        color  = color_map.get(opt, COLOR_WHITE)
        box    = pygame.Rect(x, y, spacing - 8, 36)
        bg     = color if is_sel else HUD_BG
        pygame.draw.rect(surface, bg,    box, border_radius=10)
        pygame.draw.rect(surface, color, box, 2, border_radius=10)
        txt_color = BLACK if is_sel else color
        _blit_text(surface, opt, get_font(14, True), txt_color,
                   box.center, center=True)


def _draw_title_snake(surface: pygame.Surface, tick: int):
    """Decorative animated snake curving across the top of the menu."""
    pts = []
    for i in range(60):
        x = 30 + i * 14
        y = 50 + int(14 * math.sin(i * 0.4 + tick * 0.06))
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        t = i / len(pts)
        color = (int(50 * (1 - t)), int(180 + 40 * t), int(80 + 60 * t))
        pygame.draw.circle(surface, color, (x, y), 5)
