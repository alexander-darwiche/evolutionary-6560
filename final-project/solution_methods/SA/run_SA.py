import argparse
import logging
import os
import random

from deap import tools

from solution_methods.helper_functions import load_parameters, load_job_shop_env
from solution_methods.SA.src.operators import (evaluate_individual, repair_precedence_constraints, variation)
from solution_methods.SA.utils import record_stats, output_dir_exp_name, results_saving
from solution_methods.SA.src.initialization import initialize_run

from plotting.drawer import plot_gantt_chart

logging.basicConfig(level=logging.INFO)
PARAM_FILE = "../../configs/SA.toml"


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

    for machine in jobShopEnv.machines:
        machine_operations = sorted(machine._processed_operations, key=lambda op: op.scheduling_information['start_time'])
        for operation in machine_operations:
            operation_start = operation.scheduling_information['start_time']
            operation_end = operation.scheduling_information['end_time']
            operation_duration = operation_end - operation_start

    # Initial population setup for Hall of Fame and statistics
    for step in range(1, kwargs['algorithm']['steps'] + 1):
        # Degrade your energy
        print(step)
        
        import pdb;pdb.set_trace()
        # Select a random operation
        random_operation = random.choice(jobShopEnv.operations)
        print("Start Time: " + str(random_operation.scheduling_information['start_time']))
        print("End Time: " + str(random_operation.scheduling_information['end_time']))
        print("Machine: " + str(random_operation.scheduling_information['machine_id']))
        machine_id = random_operation.scheduling_information['machine_id']
        start = random_operation.scheduling_information['start_time']
        end = random_operation.scheduling_information['end_time']

        # Determine all possible places that neighbor operations
        machine = jobShopEnv.get_machine(machine_id)
        machine_operations = sorted(machine._processed_operations, key=lambda op: op.scheduling_information['start_time'])

        for operation in machine_operations:
            if operation.scheduling_information['start_time'] < start:
                element = operation
        
        print("Start Time: " + str(element.scheduling_information['start_time']))
        print("End Time: " + str(element.scheduling_information['end_time']))
        print("Machine: " + str(element.scheduling_information['machine_id']))
        element_start = random_operation.scheduling_information['start_time']
        element_end = random_operation.scheduling_information['end_time']

        # Swap operation with randomly selected location
        machine.unschedule_operation(random_operation)
        machine.unschedule_operation(element)

        machine.add_operation_to_schedule_backfilling(random_operation,end-start, jobShopEnv._sequence_dependent_setup_times)
        machine.add_operation_to_schedule_backfilling(element,element_end-element_start, jobShopEnv._sequence_dependent_setup_times)
        
        # Update Hall of Fame and statistics with the new generation
        

        # Evaluate "new" schedule

        # Swap to new schedule if better, with some probability
        # Schedule A: 100
        # Schedule B: 105
        # You choose schedule B, 75% + (1/energy)