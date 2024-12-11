import argparse
import logging
import os
import random

from deap import tools
from collections import defaultdict
from copy import deepcopy
import math

from solution_methods.helper_functions import load_parameters, load_job_shop_env
from solution_methods.SA.src.operators import (evaluate_individual, repair_precedence_constraints, variation)
from solution_methods.SA.utils import record_stats, output_dir_exp_name, results_saving
from solution_methods.SA.src.initialization import initialize_run
import numpy as np
import matplotlib.pyplot as plt

from plotting.drawer import plot_gantt_chart

logging.basicConfig(level=logging.INFO)
PARAM_FILE = "../../configs/SA.toml"


def run_SA(jobShopEnv, **kwargs):

    total_swaps = 0
    jobShopEnv.fitness = list()
    # Initial population setup for Hall of Fame and statistics
    for step in range(1, kwargs['algorithm']['steps'] + 1):
        # Degrade your energy
        
        # # Select a random operation
        choices = jobShopEnv.choices
        machine_choices = jobShopEnv.machine_choices

        # Simulated Annealing Swaps to propose
        for i in range(0,5):
            choices, machine_choices = sim_anneal_swap(choices, machine_choices)
        
        # Randomly assign operations to machines
        counter = 0

        simEnv = deepcopy(jobShopEnv)
        simEnv.reset()
        simEnv.update_operations_available_for_scheduling()

        while len(simEnv.operations_to_be_scheduled) > 0:
            op_id = next(
                (i.operation_id for i in simEnv.operations_available_for_scheduling
                if i.job_id == choices[counter]),
                None  # Default value if no match is found
            )
            try:
                operation = simEnv.get_operation(op_id)
            except: import pdb;pdb.set_trace()
            machine_id = random.choice(list(operation.processing_times.keys()))
            duration = operation.processing_times[machine_id]
            simEnv.schedule_operation_on_machine(operation, machine_id, duration)
            simEnv.update_operations_available_for_scheduling()
            counter = counter+1

        # Update choices
        simEnv.choices = choices
        simEnv.machine_choices = machine_choices

        # plot = plot_gantt_chart(jobShopEnv)
        # plot.show()
        import math

        # Temperature based on the schedule
        temperature = temp(kwargs['algorithm']['steps'],step)
        
        # Difference in the 2 schedules
        difference = simEnv.makespan - jobShopEnv.makespan
        if difference < 0 or random.random() < (temperature*((jobShopEnv.makespan/100)/np.max([1,abs(difference)]))):
            jobShopEnv = deepcopy(simEnv)
            total_swaps = total_swaps+1

        if step%100 == 0:
            print("Temperature: "+str(temperature*((jobShopEnv.makespan/100)/np.max([1,abs(difference)]))))
            print('Step: ',str(step))
            print('Makespan:', jobShopEnv.makespan)
            print('Total Swaps: ',str(total_swaps))
        

        jobShopEnv.fitness.append(jobShopEnv.makespan)

    plot = plot_gantt_chart(jobShopEnv)
    plot.show()

    # Plot the values
    plt.plot(jobShopEnv.fitness)
    plt.xlabel('Step')
    plt.ylabel('Value')
    plt.title('Plot of Values')
    plt.grid(True)
    plt.show()
    return jobShopEnv


def sim_anneal_swap(choices, machine_choices):

    # Randomly select two distinct indices for operations on the same machine, this will ideally swap the order of operation on the machine.
    def find_duplicate_indices(lst):
        # Create a dictionary to store indices of each value
        value_indices = defaultdict(list)
        for idx, value in enumerate(lst):
            value_indices[value].append(idx)
        
        # Filter and return only the values with more than one index
        duplicates = {value: indices for value, indices in value_indices.items() if len(indices) > 0}
        return duplicates

    random_machine = random.choice(np.unique(machine_choices))
    try:
        decision_indices = find_duplicate_indices(machine_choices)[random_machine]
    except:
        import pdb;pdb.set_trace()
    swap = False
    if len(decision_indices) > 1:
        while swap == False:
            index_to_swap1 = random.randint(0, len(decision_indices) - 2)
            index_to_swap2 = index_to_swap1 + 1
            decision_index1 = decision_indices[index_to_swap1]
            decision_index2 = decision_indices[index_to_swap2]
            if (choices[decision_index1] != choices[decision_index2]):
                # Swap the values
                choices[decision_index1], choices[decision_index2] = choices[decision_index2], choices[decision_index1]
                machine_choices[decision_index1], machine_choices[decision_index2] = machine_choices[decision_index2], machine_choices[decision_index1] 
                swap = True
        
    return choices, machine_choices


# Temperature Schedule
def temp(total_steps,current_step):
    # Decay from 0.1 to 0 for the remaining steps
    decay_ratio = (current_step - 0.1 * total_steps) / (0.9 * total_steps)
    return 0.1 * (1 - decay_ratio)