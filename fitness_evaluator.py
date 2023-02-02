from abc import abstractmethod


class FitnessEvaluator:
    @abstractmethod
    def get_fitness(self, metrics: list[int]): pass


class WeightedEvaluator(FitnessEvaluator):
    COMBO_SCORE = {3: 30, 4: 80, 5: 140, 6: 200, 7: 300, 8: 400, 9: 500, 10: 600, 11: 800, 12: 1000}
    CHAIN_SCORE = {2: 100, 3: 150, 4: 200, 5: 300, 6: 400, 7: 500, 8: 700,
                   9: 900, 10: 1100, 11: 1300, 12: 1500, 13: 1800}

    def get_fitness(self, metrics: list[int]):
        combos, chain, tallest, roughness, num_moves = metrics[:10], metrics[10], metrics[11], metrics[12], metrics[13]
        chain_score = sum(self.CHAIN_SCORE.get(c, 0) for c in range(chain))
        combo_score = sum(self.COMBO_SCORE.get(c, 0) for c in combos)
        return chain_score + combo_score - pow(tallest, 3) - pow(roughness, 2) - pow(1.5, num_moves)
