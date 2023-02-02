from game.bsnes_game import Game
from agent.tetris_agent import TetrisAgent
from agent.evaluators.weighted_evaluator import WeightedEvaluator


def main():
    game = Game()
    agent = TetrisAgent(game, WeightedEvaluator())
    while True:
        score = agent.play_game()
        print(f"Game over, final score: {score}")


if __name__ == "__main__":
    main()
