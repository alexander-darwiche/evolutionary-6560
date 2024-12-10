import argparse
import logging
import os
import random

from deap import tools

from solution_methods.helper_functions import load_parameters, load_job_shop_env
from solution_methods.SA.src.operators import (evaluate_individual, repair_precedence_constraints, variation)
from solution_methods.SA.utils import record_stats, output_dir_exp_name, results_saving
from solution_methods.SA.src.initialization import initialize_run
import numpy as np

from plotting.drawer import plot_gantt_chart

logging.basicConfig(level=logging.INFO)
PARAM_FILE = "../../configs/SA.toml"


def run_SA(jobShopEnv, **kwargs):
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
        
        # # Select a random operation
        choices = jobShopEnv.choices
        
        # Copy JobShopEnv
        from copy import deepcopy
        
        # Randomly select two distinct indices
        try:
            index1 = random.randint(0, len(choices) - 2)  # Ensure there's a next index
            index2 = index1 + 1
        except:
            import pdb;pdb.set_trace()

        # Swap the values
        choices[index1], choices[index2] = choices[index2], choices[index1]

        # Randomly assign operations to machines
        counter = 0

        simEnv = deepcopy(jobShopEnv)
        simEnv.reset()
        simEnv.update_operations_available_for_scheduling()

        while len(simEnv.operations_to_be_scheduled) > 0:
            # operation = jobShopEnv.get_operation(choices[counter])
            op_id = next(
                (i.operation_id for i in simEnv.operations_available_for_scheduling
                if i.job_id == choices[counter]),
                None  # Default value if no match is found
            )
            operation = simEnv.get_operation(op_id)
            machine_id = random.choice(list(operation.processing_times.keys()))
            duration = operation.processing_times[machine_id]
            try:
                simEnv.schedule_operation_on_machine(operation, machine_id, duration)
            except:
                import pdb;pdb.set_trace()
            simEnv.update_operations_available_for_scheduling()
            counter = counter+1

        simEnv.choices = choices

        

        # Temperature schedule (example: exponential decay)
        def temperature_schedule(t):
            return max(1e-3, 10 * np.exp(-0.03 * t))
        
        # Temperature based on the schedule
        temperature = temperature_schedule(step)

        # Difference in the 2 schedules
        difference = simEnv.makespan - jobShopEnv.makespan
        if difference < 0: #or random.random() < np.exp((difference) / temperature):
            jobShopEnv = deepcopy(simEnv)
            # print('Swap occured on Step: ', step)
            # print('Makespan:', jobShopEnv.makespan)
        
        if step%100 == 0:
            print('Step: ',str(step))
            print('Makespan:', jobShopEnv.makespan)
        # plot = plot_gantt_chart(jobShopEnv)
        # plot.show(block=False)