# =============================================================================
# constants.py — All game-wide constants
# =============================================================================

# ── Window ────────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 900
WINDOW_HEIGHT = 700
TITLE         = "Snake Game"
FPS           = 60

# ── Grid ──────────────────────────────────────────────────────────────────────
CELL_SIZE    = 24          # px per grid cell
GRID_COLS    = 30          # (900 - 60) / 24 ... we offset the play area below
GRID_ROWS    = 24          # (700 - 100 - 20) / 24
GRID_OFFSET_X = 30         # left margin of the grid
GRID_OFFSET_Y = 90         # top margin (leaves room for HUD)

# Derived play-area pixel boundaries
PLAY_W = GRID_COLS * CELL_SIZE   # 720
PLAY_H = GRID_ROWS * CELL_SIZE   # 576

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GRAY         = (80,  80,  80)
DARK_GRAY    = (30,  30,  30)
LIGHT_GRAY   = (160, 160, 160)

# Background gradient stops
BG_TOP       = (10,  15,  30)
BG_BOTTOM    = (5,   10,  20)

# Grid line color
GRID_COLOR   = (20,  30,  50)

# HUD / UI
HUD_BG       = (8,   12,  25)
BORDER_COLOR = (0,   180, 120)

# Snake skins: (head_color, body_color, glow_color)
SNAKE_SKINS = {
    "Classic": ((50, 220, 100), (30, 160, 70),  (0, 255, 100)),
    "Neon":    ((0,  230, 255), (0,  140, 200), (0, 200, 255)),
    "Lava":    ((255, 90,  30), (200, 40,  10), (255, 130, 0)),
    "Royal":   ((160, 60, 255), (100, 20, 200), (200, 100, 255)),
}

# Food
FOOD_COLOR        = (255, 60,  80)
FOOD_GLOW         = (255, 120, 120)
GOLDEN_COLOR      = (255, 210, 0)
GOLDEN_GLOW       = (255, 240, 100)

# Power-up colors
PU_SPEED_COLOR    = (255, 165, 0)    # orange  — Speed Boost
PU_SLOW_COLOR     = (0,   160, 255)  # blue    — Slow Motion
PU_DOUBLE_COLOR   = (180, 0,   255)  # purple  — Double Score

# Text / UI
COLOR_TITLE       = (0,   255, 180)
COLOR_SUBTITLE    = (160, 255, 200)
COLOR_WHITE       = WHITE
COLOR_YELLOW      = (255, 230, 0)
COLOR_RED         = (255, 60,  60)
COLOR_GREEN       = (50,  220, 100)
COLOR_ORANGE      = (255, 165, 0)
COLOR_PURPLE      = (180, 0,   255)
COLOR_CYAN        = (0,   230, 255)

# ── Gameplay ──────────────────────────────────────────────────────────────────
# Base moves per second for each difficulty
DIFFICULTY_SPEEDS = {
    "Easy":   6,
    "Medium": 10,
    "Hard":   16,
}
# Frames between moves = FPS / moves_per_second
# Speed increases by 1 move/s every SPEED_UP_EVERY points (capped at MAX_MPS)
SPEED_UP_EVERY    = 5       # points
MAX_MPS           = 24      # max moves per second

# Power-up durations (in game ticks, i.e. snake moves)
PU_DURATION       = 40      # ticks
# How often a power-up spawns (every N food eaten)
PU_SPAWN_EVERY    = 5
# How often golden food appears (every N food eaten)
GOLDEN_EVERY      = 8

# Scoring
BASE_SCORE        = 10      # points per normal food
GOLDEN_SCORE      = 50      # points for golden food
COMBO_WINDOW      = 3       # seconds between eats to keep combo alive
COMBO_MULTIPLIER  = 0.5     # each extra combo level adds 50 % of base

# Countdown seconds before game starts
COUNTDOWN_SECS    = 3

# Particle settings
PARTICLE_COUNT    = 18
PARTICLE_LIFETIME = 45      # frames
