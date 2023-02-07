from game.bsnes_game import Game
from agent.tetris_agent import TetrisAgent
from agent.evaluators.weighted_evaluator import WeightedEvaluator
from agent.evaluators.ai_evaluator import AiEvaluator


def main():
    evaluator = AiEvaluator('model1675461712.375189')
    # evaluator = WeightedEvaluator()
    game = Game()
    agent = TetrisAgent(game, evaluator)
    while True:
        score = agent.play_game(60)
        game.change_save_state()
        print(f"Game over, final score: {score}")


if __name__ == "__main__":
    main()
