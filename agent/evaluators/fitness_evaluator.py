from abc import abstractmethod


class FitnessEvaluator:
    @abstractmethod
    def get_fitness(self, metrics: list[int]): pass
