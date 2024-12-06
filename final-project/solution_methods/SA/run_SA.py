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


def run_SA(jobShopEnv, individual, toolbox, stats, hof, **kwargs):
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
    hof.update(individual)

    gen = 0
    logbook = tools.Logbook()
    logbook.header = ["gen"] + (stats.fields if stats else [])
    df_list = []

    # Initial statistics recording
    record_stats(gen, individual, logbook, stats, kwargs['output']['logbook'], df_list, logging)
    if kwargs['output']['logbook']:
        logging.info(logbook.stream)

    for gen in range(1, kwargs['algorithm']['ngen'] + 1):
        # Vary the population
        offspring = variation(individual, toolbox,
                              pop_size=kwargs['algorithm'].get('population_size'),
                              cr = kwargs['algorithm'].get('cr'),
                              indpb = kwargs['algorithm'].get('indpb'))

        # Repair precedence constraints if the environment requires it (only for assembly scheduling (fajsp))
        if any(keyword in jobShopEnv.instance_name for keyword in ['/dafjs/', '/yfjs/']):
            try:
                offspring = repair_precedence_constraints(jobShopEnv, offspring)
            except Exception as e:
                logging.error(f"Error repairing precedence constraints: {e}")
                continue

        # Evaluate offspring fitness
        try:
            fitnesses = evaluate_population(toolbox, offspring)
            for ind, fit in zip(offspring, fitnesses):
                ind.fitness.values = fit
        except Exception as e:
            logging.error(f"Error evaluating offspring fitness: {e}")
            continue

        # Select the next generation
        individual[:] = toolbox.select(individual + offspring)

        # Update Hall of Fame and statistics with the new generation
        hof.update(individual)
        record_stats(gen, individual, logbook, stats, kwargs['output']['logbook'], df_list, logging)
   
    makespan, jobShopEnv = evaluate_individual(hof[0], jobShopEnv, reset=False)
    logging.info(f"Makespan: {makespan}")
    return makespan, jobShopEnv