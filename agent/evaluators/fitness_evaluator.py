from abc import abstractmethod


class FitnessEvaluator:
    def __init__(self):
        self.metrics = None

    @abstractmethod
    def get_fitness(self, metrics: list[int]) -> float: pass

    @abstractmethod
    def should_raise(self, metrics: list[int]) -> bool: pass
