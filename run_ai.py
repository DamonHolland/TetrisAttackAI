from bsnes_game import Game
from tetris_agent import TetrisAgent
from fitness_evaluator import WeightedEvaluator


def main():
    game = Game()
    agent = TetrisAgent(game, WeightedEvaluator())
    while True:
        score = agent.play_game()
        print(f"Game over, final score: {score}")


if __name__ == "__main__":
    main()
