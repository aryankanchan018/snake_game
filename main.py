# =============================================================================
# main.py — Entry point for the Snake Game
#
# Install dependencies:
#   pip install -r requirements.txt
#
# Run:
#   python main.py
# =============================================================================

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
