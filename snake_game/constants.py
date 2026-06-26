# =============================================================================
# snake_game/constants.py — All game-wide constants
# =============================================================================

import os

# Root paths
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")

# ── Window ────────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 900
WINDOW_HEIGHT = 700
TITLE         = "Snake Game"
FPS           = 60

# ── Grid ──────────────────────────────────────────────────────────────────────
CELL_SIZE     = 24
GRID_COLS     = 30
GRID_ROWS     = 24
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 90

PLAY_W = GRID_COLS * CELL_SIZE   # 720
PLAY_H = GRID_ROWS * CELL_SIZE   # 576

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (80,  80,  80)
DARK_GRAY  = (30,  30,  30)
LIGHT_GRAY = (160, 160, 160)

BG_TOP     = (10,  15,  30)
BG_BOTTOM  = (5,   10,  20)

GRID_COLOR   = (20,  30,  50)
HUD_BG       = (8,   12,  25)
BORDER_COLOR = (0,   180, 120)

# Snake skins: (head_color, body_color, glow_color)
SNAKE_SKINS = {
    "Classic": ((50,  220, 100), (30,  160, 70),  (0,   255, 100)),
    "Neon":    ((0,   230, 255), (0,   140, 200), (0,   200, 255)),
    "Lava":    ((255, 90,  30),  (200, 40,  10),  (255, 130, 0)),
    "Royal":   ((160, 60,  255), (100, 20,  200), (200, 100, 255)),
}

# Food
FOOD_COLOR   = (255, 60,  80)
FOOD_GLOW    = (255, 120, 120)
GOLDEN_COLOR = (255, 210, 0)
GOLDEN_GLOW  = (255, 240, 100)

# Power-up colors
PU_SPEED_COLOR  = (255, 165, 0)
PU_SLOW_COLOR   = (0,   160, 255)
PU_DOUBLE_COLOR = (180, 0,   255)

# Text / UI colors
COLOR_TITLE    = (0,   255, 180)
COLOR_SUBTITLE = (160, 255, 200)
COLOR_WHITE    = WHITE
COLOR_YELLOW   = (255, 230, 0)
COLOR_RED      = (255, 60,  60)
COLOR_GREEN    = (50,  220, 100)
COLOR_ORANGE   = (255, 165, 0)
COLOR_PURPLE   = (180, 0,   255)
COLOR_CYAN     = (0,   230, 255)

# ── Gameplay ──────────────────────────────────────────────────────────────────
DIFFICULTY_SPEEDS = {
    "Easy":   6,
    "Medium": 10,
    "Hard":   16,
}

SPEED_UP_EVERY = 5    # score points before each speed increase
MAX_MPS        = 24   # max moves per second

PU_DURATION    = 40   # power-up active ticks (snake moves)
PU_SPAWN_EVERY = 5    # spawn power-up every N food eaten
GOLDEN_EVERY   = 8    # spawn golden food every N food eaten

BASE_SCORE      = 10
GOLDEN_SCORE    = 50
COMBO_WINDOW    = 3.0  # seconds between eats to maintain combo
COMBO_MULTIPLIER = 0.5 # +50% score per extra combo level

COUNTDOWN_SECS = 3

PARTICLE_COUNT    = 18
PARTICLE_LIFETIME = 45  # frames
