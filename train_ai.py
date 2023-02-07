import time

import pygad
import pygad.kerasga

from agent.evaluators.ai_evaluator import AiEvaluator
from agent.tetris_agent import TetrisAgent
from game.bsnes_game import Game


def fitness_func(solution, _):
    global agent
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=agent.evaluator.model, weights_vector=solution)
    agent.evaluator.set_weights(model_weights_matrix)
    return agent.play_game(60)


def callback_generation(instance):
    global agent
    print(f" Generation {instance.generations_completed} Complete ".center(30, '-'))
    agent.game.change_save_state()


def main():
    keras_ga = pygad.kerasga.KerasGA(model=agent.evaluator.model, num_solutions=10)
    ga_instance = pygad.GA(num_generations=30, num_parents_mating=2,
                           initial_population=keras_ga.population_weights,
                           fitness_func=fitness_func, on_generation=callback_generation)
    ga_instance.run()
    s, f, i = ga_instance.best_solution()
    best_solution_weights = pygad.kerasga.model_weights_as_matrix(model=agent.evaluator.model, weights_vector=s)
    agent.evaluator.set_weights(best_solution_weights)
    agent.evaluator.model.save('./models/model' + str(time.time()) + '.h5')
    ga_instance.plot_fitness(title="Tetris Attack AI Agent Fitness", linewidth=4)


if __name__ == "__main__":
    agent = TetrisAgent(Game(), AiEvaluator())
    main()
