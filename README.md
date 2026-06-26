# 🐍 Snake Game

A modern, feature-rich Snake Game built with **Python** and **Pygame** — featuring glow effects, power-ups, particle bursts, combo scoring, persistent stats, and an animated menu.

---

## 🎮 Preview

```
Arrow Keys → Move    |    P → Pause    |    R → Restart    |    ESC → Quit
```

---

## ✨ Features

| Category | Details |
|---|---|
| 🎨 Visuals | Gradient background, glowing snake head, pulsing food, particle bursts |
| ⚡ Power-ups | Speed Boost, Slow Motion, Double Score — spawns every 5 foods |
| ⭐ Golden Food | Appears every 8 foods, worth 50 pts with rotating star animation |
| 🔥 Combo System | Eat within 3 s to chain multipliers (+50% per level) |
| 🐍 Snake Skins | Classic, Neon, Lava, Royal |
| 🎚️ Difficulty | Easy / Medium / Hard with auto speed scaling |
| 💾 Persistence | High score, games played, food eaten, longest snake saved to `data/stats.json` |
| 🔊 Sounds | Procedurally synthesised — no audio files needed |
| 📊 Stats Screen | Full lifetime statistics screen |

---

## 📁 Project Structure

```
snake_game/
├── main.py                  # Entry point — run this
├── requirements.txt
├── README.md
├── .gitignore
├── snake_game/              # Game package
│   ├── __init__.py
│   ├── constants.py         # Colors, speeds, grid config
│   ├── snake.py             # Snake movement, rendering, glow eyes
│   ├── food.py              # Food, GoldenFood, PowerUp entities
│   ├── particles.py         # Particle burst system
│   ├── score_manager.py     # JSON-based persistent statistics
│   ├── ui.py                # All screens: menu, HUD, pause, game over
│   └── game.py              # Game state machine + main loop
└── data/
    └── stats.json           # Auto-created on first run (gitignored)
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/aryankanchan018/snake_game.git
cd snake_game
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the game

```bash
python main.py
```

> Requires **Python 3.10+** and **pygame 2.1+**

---

## 🕹️ Controls

| Key | Action |
|---|---|
| Arrow Keys | Move snake |
| P | Pause / Resume |
| R | Restart |
| ESC | Quit / Back to Menu |
| S (menu) | Open Statistics |
| ← → (menu) | Change difficulty |
| ↑ ↓ (menu) | Change skin |
| Enter / Space | Start game |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Pygame 2.6**
- No external assets — all sounds and visuals are generated in code

---

## 📜 License

MIT License — free to use, modify, and distribute.
