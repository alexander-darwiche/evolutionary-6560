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

    # for machine in jobShopEnv.machines:
    #     machine_operations = sorted(machine._processed_operations, key=lambda op: op.scheduling_information['start_time'])
    #     for operation in machine_operations:
    #         operation_start = operation.scheduling_information['start_time']
    #         operation_end = operation.scheduling_information['end_time']
    #         operation_duration = operation_end - operation_start

    # Initial population setup for Hall of Fame and statistics
    for step in range(1, kwargs['algorithm']['steps'] + 1):
        # Degrade your energy
        print(step)
        
        # # Select a random operation
        # random_operation = random.choice(jobShopEnv.operations)

        # machine_id = random_operation.scheduling_information['machine_id']
        # start = random_operation.scheduling_information['start_time']
        # end = random_operation.scheduling_information['end_time']

        # # Determine all possible places that neighbor operations
        # machine = jobShopEnv.get_machine(machine_id)
        # machine_operations = sorted(machine._processed_operations, key=lambda op: op.scheduling_information['start_time'])

        # before_flag = False
        # for operation in machine_operations:
        #     if operation.scheduling_information['start_time'] < start:
        #         element = operation
        #         before_flag = True
        
        # end_flag = False
        # counter = 0
        # for operation in machine_operations:
        #     if operation.scheduling_information['start_time'] > start:
        #         if counter == 0:
        #             element2 = operation
        #             end_flag = True
        #             counter = counter + 1


        # # Swap operation with randomly selected location
        # try:
        #     if before_flag:
        #         print("Swapping on machine: ",str(machine_id))
        #         element_start = element.scheduling_information['start_time']
        #         element_end = element.scheduling_information['end_time']
        #         machine.unschedule_operation(random_operation)
        #         machine.unschedule_operation(element)

        #         machine.add_operation_to_schedule(random_operation,end-start, jobShopEnv._sequence_dependent_setup_times)
        #         machine.add_operation_to_schedule(element,element_end-element_start, jobShopEnv._sequence_dependent_setup_times)
        #     elif end_flag:
        #         print("Swapping on machine: ",str(machine_id))
        #         element_start2 = element2.scheduling_information['start_time']
        #         element_end2 = element2.scheduling_information['end_time']
        #         machine.unschedule_operation(random_operation)
        #         machine.unschedule_operation(element2)

        #         machine.add_operation_to_schedule(element2,element_end2-element_start2, jobShopEnv._sequence_dependent_setup_times)
        #         machine.add_operation_to_schedule(random_operation,end-start, jobShopEnv._sequence_dependent_setup_times)
        # except:
        #     import pdb;pdb.set_trace()

        # # jobShopEnv.repair
        choices = jobShopEnv.choices
        # Randomly select two distinct indices
        try:
            index1 = random.randint(0, len(choices) - 2)  # Ensure there's a next index
            index2 = index1 + 1
        except:
            import pdb;pdb.set_trace()

        # Swap the values
        choices[index1], choices[index2] = choices[index2], choices[index1]

        print(index1)
        print(index2)
        # Randomly assign operations to machines
        counter = 0
        jobShopEnv.reset()
        jobShopEnv.update_operations_available_for_scheduling()
        import pdb;pdb.set_trace()
        while len(jobShopEnv.operations_to_be_scheduled) > 0:
            # operation = jobShopEnv.get_operation(choices[counter])
            operation = random.choice(jobShopEnv.operations_available_for_scheduling)
            machine_id = random.choice(list(operation.processing_times.keys()))
            duration = operation.processing_times[machine_id]
            try:
                jobShopEnv.schedule_operation_on_machine(operation, machine_id, duration)
            except:
                import pdb;pdb.set_trace()
            jobShopEnv.update_operations_available_for_scheduling()
            counter = counter+1

        jobShopEnv.choices = choices

        print('Makespan:', jobShopEnv.makespan)

        # plot = plot_gantt_chart(jobShopEnv)
        # plot.show(block=False)

        # import pdb;pdb.set_trace()
        # Update Hall of Fame and statistics with the new generation


        # Evaluate "new" schedule

        # Swap to new schedule if better, with some probability
        # Schedule A: 100
        # Schedule B: 105
        # You choose schedule B, 75% + (1/energy)