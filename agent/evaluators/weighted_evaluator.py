import sys

from agent.evaluators.fitness_evaluator import FitnessEvaluator


class WeightedEvaluator(FitnessEvaluator):
    COMBO_SCORE = {3: 30, 4: 80, 5: 140, 6: 200, 7: 300, 8: 400, 9: 500, 10: 600, 11: 800, 12: 1000}
    CHAIN_SCORE = {2: 100, 3: 150, 4: 200, 5: 300, 6: 400, 7: 500, 8: 700,
                   9: 900, 10: 1100, 11: 1300, 12: 1500, 13: 1800}

    def get_fitness(self, metrics: list[int]) -> float:
        combos, chain, tallest = metrics[:5], metrics[5], metrics[6]
        roughness, total_blocks, move_count = metrics[7], metrics[8], metrics[9]
        chain_score = sum(self.CHAIN_SCORE.get(c, 0) for c in range(chain))
        combo_score = sum(self.COMBO_SCORE.get(c, 0) for c in combos)
        weighted_fitness = chain_score + combo_score - pow(tallest, 3) - pow(roughness, 2)
        if move_count > 30:
            return -sys.maxsize
        return weighted_fitness

    def should_raise(self, metrics: list[int]) -> bool:
        chain, tallest, roughness = metrics[5], metrics[6], metrics[7]
        total_blocks, move_count, game_stopped = metrics[8], metrics[9], metrics[10]
        if not chain and roughness < 5 and total_blocks < 30 and tallest < 6:
            return True
        if game_stopped and not move_count:
            return True
        return False
