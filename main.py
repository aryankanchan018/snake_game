# =============================================================================
# main.py — Entry point
#
# Install:  pip install -r requirements.txt
# Run:      python main.py
# =============================================================================

from snake_game.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
