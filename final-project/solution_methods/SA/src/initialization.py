import logging

import multiprocessing

# from multiprocessing.pool import Pool

import numpy as np
from deap import base, creator, tools

from solution_methods.SA.src.operators import (
    evaluate_individual, init_individual)
from solution_methods.helper_functions import set_seeds


def initialize_run(jobShopEnv, **kwargs):
    """
    Initializes the GA run by setting up the DEAP toolbox, statistics, hall of fame, and initial population.

    Args:
        jobShopEnv: The job shop environment to be optimized.
        pool: Multiprocessing pool for parallel processing.
        kwargs: Additional keyword arguments for setting algorithm parameters.

    Returns:
        tuple: (initial_population, toolbox, stats, hof)
            - initial_population: Initialized population.
            - toolbox: DEAP toolbox with registered operators.
            - stats: Statistics object for tracking evolution progress.
            - hof: Hall of fame to store the best individuals.
    """

    
    # Set random seed
    set_seeds(kwargs["algorithm"].get("seed", None))

    # Initialize logging if not already configured
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO)

    # try:
    #initial_population = init_population(toolbox, kwargs['algorithm']['population_size'], )
    individual = init_individual(jobShopEnv)
    fitness, jobShopEnv = evaluate_individual(individual, jobShopEnv)

    return individual, fitness
