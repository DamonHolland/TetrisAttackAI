import os

import numpy
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow

from agent.evaluators.fitness_evaluator import FitnessEvaluator
from agent.training.lite_model import LiteModel


class AiEvaluator(FitnessEvaluator):
    def __init__(self, model_name: str = None):
        if model_name:
            self.model = tensorflow.keras.models.load_model(f'./agent/training/models/{model_name}.h5')
            self._lite_model = LiteModel.from_keras_model(self.model)
            self._weights_set = True
        else:
            input_layer = tensorflow.keras.layers.Input(11)
            dense_layer1 = tensorflow.keras.layers.Dense(16, activation="relu")(input_layer)
            dense_layer2 = tensorflow.keras.layers.Dense(16, activation="relu")(dense_layer1)
            fitness_output = tensorflow.keras.layers.Dense(1, activation="linear")(dense_layer2)
            concatenated = tensorflow.keras.layers.Concatenate()([fitness_output, input_layer])
            dense_layer3 = tensorflow.keras.layers.Dense(16, activation="relu")(concatenated)
            dense_layer4 = tensorflow.keras.layers.Dense(16, activation="relu")(dense_layer3)
            raise_output = tensorflow.keras.layers.Dense(1, activation="sigmoid")(dense_layer4)
            self.model = tensorflow.keras.Model(inputs=input_layer, outputs=[fitness_output, raise_output])
            self._lite_model = LiteModel.from_keras_model(self.model)
            self._weights_set = False
        super().__init__()

    def set_weights(self, weights):
        self.model.set_weights(weights)
        self._lite_model = LiteModel.from_keras_model(self.model)
        self._weights_set = True

    def get_fitness(self, metrics: list[int]):
        if not self._weights_set:
            raise RuntimeError("Required to set weights before using keras model")
        return self._lite_model.predict_single(numpy.array(metrics))[0][0]

    def should_raise(self, metrics: list[int]) -> bool:
        if not self._weights_set:
            raise RuntimeError("Required to set weights before using keras model")
        return self._lite_model.predict_single(numpy.array(metrics))[1][0] > 0.5
