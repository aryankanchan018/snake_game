# =============================================================================
# main.py — Entry point (Pygbag-compatible async loop)
#
# Local:   python main.py
# Web:     pygbag main.py  (builds to web/index.html)
# =============================================================================

import asyncio
import pygame
from snake_game.game import Game


async def main():
    game = Game()

    # Pygbag requires the main loop to yield control each frame via asyncio.sleep(0)
    while True:
        game.tick()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
