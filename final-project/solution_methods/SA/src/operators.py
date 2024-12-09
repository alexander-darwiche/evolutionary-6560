import random

import numpy as np

from scheduling_environment.jobShop import JobShop
from scheduling_environment.operation import Operation
from solution_methods.GA.src.heuristics import global_load_balancing_scheduler, local_load_balancing_scheduler, random_scheduler


def select_next_operation_from_job(jobShopEnv: JobShop, job_id) -> Operation:
    # select next operation for job
    for operation in jobShopEnv.operations_available_for_scheduling:
        if operation.job_id == job_id:
            return operation
        
# Initialize an individual for the genetic algorithm (with random actions selection heuristic)
def init_individual(jobShopEnv):
    """create individual, indivial is a list of machine selection (ix of options) and operation sequence (ix of job)"""

    rand = random.random()
    if rand <= 0.6:  # 60% initial assignment with global selection scheduler
        jobShopEnv = global_load_balancing_scheduler(jobShopEnv)
    elif rand <= 0.9:  # 30% initial assignment with local selection scheduler
        jobShopEnv = local_load_balancing_scheduler(jobShopEnv)
    else:  # 10% initial assignment with random scheduler
        jobShopEnv = random_scheduler(jobShopEnv)
    # get the operation sequence and machine allocation lists
    operation_sequence = [operation.job_id for operation in jobShopEnv.scheduled_operations]
    machine_selection = [(operation.operation_id, sorted(list(operation.processing_times.keys())).index(operation.scheduled_machine)) for operation in jobShopEnv.scheduled_operations]
    machine_selection.sort()
    machine_selection = [allocation for _, allocation in machine_selection]
    jobShopEnv.reset()
    return [machine_selection, operation_sequence]

def evaluate_individual(individual, jobShopEnv: JobShop, reset=True):
    jobShopEnv.reset()
    jobShopEnv.update_operations_available_for_scheduling()
    for i in range(len(individual[0])):
        job_id = individual[1][i]
        operation = select_next_operation_from_job(jobShopEnv, job_id)
        operation_option_index = individual[0][operation.operation_id]
        machine_id = sorted(operation.processing_times.keys())[operation_option_index]
        duration = operation.processing_times[machine_id]

        jobShopEnv.schedule_operation_with_backfilling(operation, machine_id, duration)
        jobShopEnv.update_operations_available_for_scheduling()

    makespan = jobShopEnv.makespan

    # if reset:
    #     jobShopEnv.reset()
    return makespan, jobShopEnv

def variation(population, toolbox, pop_size, cr, indpb):
    offspring = []
    for _ in range(int(pop_size)):
        op_choice = random.random()
        if op_choice < cr:  # Apply crossover
            ind1, ind2 = list(map(toolbox.clone, random.sample(population, 2)))
            if random.random() < 0.5:
                ind1[0], ind2[0] = toolbox.mate_TwoPoint(ind1[0], ind2[0])
            else:
                ind1[0], ind2[0] = toolbox.mate_Uniform(ind1[0], ind2[0])
            
            has_non_zero = any(x != 0 for x in ind1[0])
            if (has_non_zero): import pdb;pdb.set_trace()
            ind1[1], ind2[1] = toolbox.mate_POX(ind1[1], ind2[1])
            del ind1.fitness.values, ind2.fitness.values

        else:  # Apply reproduction
            ind1 = toolbox.clone(random.choice(population))
            # ind2 = toolbox.clone(random.choice(population))

        # Apply mutation
        ind1[0] = toolbox.mutate_machine_selection(ind1[0], indpb)
        ind1[1] = toolbox.mutate_operation_sequence(ind1[1], indpb)
        # ind2[0] = toolbox.mutate_machine_selection(ind2[0])
        # ind2[1] = toolbox.mutate_operation_sequence(ind2[1])

        del ind1.fitness.values
        # del ind2.fitness.values
        offspring.append(ind1)
        # offspring.append(ind2)

    return offspring


def repair_precedence_constraints(env, offspring):
    precedence_relations = env.precedence_relations_jobs
    for ind in offspring:
        i = 0
        lst = ind[1]
        while i < len(ind[1]):
            # print(i)
            if lst[i] in precedence_relations.keys():
                max_index = 0
                for j in precedence_relations[lst[i]]:
                    index = len(lst) - 1 - lst[::-1].index(j)
                    if index > max_index:
                        max_index = index
                if max_index > i:
                    item = lst[i]
                    lst.pop(i)  # Remove the item from the source index
                    lst.insert(max_index, item)
                    # print(lst)
                    continue
            i += 1
    return offspring
