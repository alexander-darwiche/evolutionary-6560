import argparse
import logging
import os

from deap import tools

from solution_methods.helper_functions import load_parameters, load_job_shop_env
from solution_methods.SA.src.operators import (evaluate_individual, evaluate_population, repair_precedence_constraints, variation)
from solution_methods.SA.utils import record_stats, output_dir_exp_name, results_saving
from solution_methods.SA.src.initialization import initialize_run

from plotting.drawer import plot_gantt_chart

logging.basicConfig(level=logging.INFO)
PARAM_FILE = "../../configs/GA.toml"


def run_SA(jobShopEnv, individual, **kwargs):
    """Executes the genetic algorithm and returns the best individual.

    Args:
        jobShopEnv: The problem environment.
        population: The initial population.
        toolbox: DEAP toolbox.
        stats: DEAP statistics.
        hof: Hall of Fame.
        kwargs: Additional keyword arguments.

    Returns:
        The best individual found by the genetic algorithm.
    """

    # Initial population setup for Hall of Fame and statistics
    for step in range(1, kwargs['algorithm']['steps'] + 1):
        # Degrade your energy

        # Select a random operation

        # Determine all possible places that operation can move

        # Swap operation with randomly selected location

        # Update Hall of Fame and statistics with the new generation

        # Evaluate "new" schedule

        # Swap to new schedule if better, with some probability
        # Schedule A: 100
        # Schedule B: 105
        # You choose schedule B, 75% + (1/energy)