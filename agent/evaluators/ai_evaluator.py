from agent.evaluators.fitness_evaluator import FitnessEvaluator


class AiEvaluator(FitnessEvaluator):

    def get_fitness(self, metrics: list[int]):
        combos, chain, tallest, roughness, move_count = metrics[:10], metrics[10], metrics[11], metrics[12], metrics[13]
