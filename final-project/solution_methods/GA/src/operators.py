import random
from collections import Counter
import numpy as np
from deap import tools
from scheduling_environment.jobShop import JobShop
from scheduling_environment.operation import Operation
from solution_methods.GA.src.heuristics import global_load_balancing_scheduler, local_load_balancing_scheduler, random_scheduler
from solution_methods.helper_functions import load_job_shop_env, load_parameters

def select_next_operation_from_job(jobShopEnv: JobShop, job_id) -> Operation:
    # select next operation for job
    for operation in jobShopEnv.operations_available_for_scheduling:
        if operation.job_id == job_id:
            return operation


def pox_crossover(ind1, ind2, nr_preserving_jobs):
    preserving_jobs = random.sample(range(1, max(ind1)), nr_preserving_jobs)

    new_sequence_ind1 = list(filter(lambda a: a not in preserving_jobs, ind2))
    for i in range(len(ind1)):
        if ind1[i] in preserving_jobs:
            new_sequence_ind1.insert(i, ind1[i])

    new_sequence_ind2 = list(filter(lambda a: a not in preserving_jobs, ind1))
    for i in range(len(ind2)):
        if ind2[i] in preserving_jobs:
            new_sequence_ind2.insert(i, ind1[i])

    return new_sequence_ind1, new_sequence_ind2


def mutate_shortest_proc_time(individual, indpb, jobShopEnv: JobShop):
    for i, _ in enumerate(individual):
        if random.random() < indpb:
            operation = jobShopEnv.operations[i]
            individual[i] = np.argmin(operation.processing_times)
    return individual


def mutate_sequence_exchange(individual, indpb):
    for i in range(len(individual)):
        if random.random() < indpb:
            j = random.choice([index for index in range(len(individual)) if index != i])
            individual[i], individual[j] = individual[j], individual[i]
    return individual


# Initialize an individual for the genetic algorithm (with random actions selection heuristic)
def init_individual(ind_class, jobShopEnv):
    """create individual, indivial is a list of machine selection (ix of options) and operation sequence (ix of job)"""

    rand = random.random()
    if rand <= 0.6:  # 60% initial assignment with global selection scheduler
        jobShopEnv = global_load_balancing_scheduler(jobShopEnv)
    elif rand <= 0.9:  # 30% initial assignment with local selection scheduler
        jobShopEnv = local_load_balancing_scheduler(jobShopEnv)
    else:  # 10% initial assignment with random scheduler
        jobShopEnv = random_scheduler(jobShopEnv)
    #import pdb;pdb.set_trace()
    # get the operation sequence and machine allocation lists
    operation_sequence = [operation.job_id for operation in jobShopEnv.scheduled_operations]
    machine_selection = [
        (operation.operation_id, sorted(list(operation.processing_times.keys())).index(operation.scheduled_machine))
        for operation in jobShopEnv.scheduled_operations]
    machine_selection.sort()
    machine_selection = [allocation for _, allocation in machine_selection]
    jobShopEnv.reset()
    return ind_class([machine_selection, operation_sequence])


# Initialize a population
def init_population(toolbox, population_size):
    return [toolbox.init_individual() for _ in range(population_size)]


def evaluate_individual(individual, jobShopEnv: JobShop, reset=True):

    jobShopEnv.reset()
    jobShopEnv.update_operations_available_for_scheduling()
    if individual == None:
        import pdb; pdb.set_trace()
    for i in range(len(individual[0])):
        try:
            job_id = individual[1][i]
            operation = select_next_operation_from_job(jobShopEnv, job_id)
            operation_option_index = individual[0][operation.operation_id] if len(sorted(operation.processing_times.keys())) - 1>= individual[0][operation.operation_id]  else 0
            
            machine_id = sorted(operation.processing_times.keys())[operation_option_index]
            duration = operation.processing_times[machine_id]

            jobShopEnv.schedule_operation_with_backfilling(operation, machine_id, duration)
            jobShopEnv.update_operations_available_for_scheduling()
        except: 
            import pdb; pdb.set_trace()

    makespan = jobShopEnv.makespan

    if reset:
        jobShopEnv.reset()
    return makespan, jobShopEnv


def evaluate_population(toolbox, population):
    # start_time = time.time()

    # sequential evaluation of population
    population = [[ind[0], ind[1]] for ind in population]
    fitnesses = [toolbox.evaluate_individual(ind) for ind in population]
    fitnesses = [(fit[0],) for fit in fitnesses]

    # parallel evaluation of population
    # population = [[ind[0], ind[1]] for ind in population]
    # fitnesses = toolbox.map(toolbox.evaluate_individual, population)
    # fitnesses = [(fit[0],) for fit in fitnesses]

    return fitnesses

def variation(population, toolbox, pop_size, cr, indpb):
    offspring = []
    for _ in range(int(pop_size)):
        op_choice = random.random()
        if op_choice < cr:  # Apply crossover
            ind1, ind2 = list(map(toolbox.clone, random.sample(population, 2)))

            # Randomly select a crossover operator
            crossover_choice = random.choice([
                "mate_TwoPoint",
                "mate_Uniform",
                "mate_POX",
                "mate_Order",
                "mate_Cycle"
            ])
            #import pdb; pdb.set_trace()
            if crossover_choice in ["mate_Order", "mate_Cycle", "mate_POX"]:
                ind1[1], ind2[1] = getattr(toolbox, crossover_choice)(ind1[1], ind2[1])
            else:
                ind1[0], ind2[0] = getattr(toolbox, crossover_choice)(ind1[0], ind2[0])

            # Validate crossover results
            if None in ind1[1] or None in ind2[1]:
                raise ValueError(f"Crossover resulted in None values: ind1={ind1}, ind2={ind2}")

            del ind1.fitness.values, ind2.fitness.values

        else:  # Apply reproduction
            ind1 = toolbox.clone(random.choice(population))

        # Randomly select a mutation operator for machine selection
        machine_mutation_choice = random.choice([
            "mutate_machine_selection",
            "mutate_Scramble",
            "mutate_Inversion"
        ])
        ind1[0] = getattr(toolbox, machine_mutation_choice)(ind1[0], indpb)

        # Randomly select a mutation operator for operation sequence
        sequence_mutation_choice = random.choice([
            "mutate_operation_sequence",
        ])
        ind1[1] = getattr(toolbox, sequence_mutation_choice)(ind1[1], indpb)

        # Validate mutation results
        if None in ind1[0] or None in ind1[1]:
            raise ValueError(f"Mutation resulted in None values: ind1={ind1}")

        del ind1.fitness.values
        offspring.append(ind1)

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

from deap import tools

def repair_child(child):     
    # Count occurrences of each value in the child    
    max_count = find_number_operations(load_job_shop_env(load_parameters("configs/GA.toml")['instance'].get('problem_instance')))
    value_range = range(len(max_count))
    value_counts = Counter(child)        
    # # Find missing and excess values    
    missing = [v for v in value_range if value_counts[v] < max_count[v]]     
    excess = [v for v in value_range if value_counts[v] > max_count[v]]         
    # Create a list of indices for excess values    
    excess_indices = [i for i, v in enumerate(child) if v in excess]         
    # Replace excess values with missing ones
    for i in excess_indices: 
        #import pdb; pdb.set_trace()
        value = child[i] 
        if value_counts[value] > max_count[value] and missing: 
            new_value = missing[0] 
            child[i] = new_value 
            value_counts[value] -= 1 
            value_counts[new_value] += 1
            if value_counts[new_value] == max_count[new_value]:
                missing.remove(new_value)
    return child

def find_number_operations(jobShopEnv: JobShop):
    counts = dict()
    for job in jobShopEnv.jobs:
        count = 0
        for operation in job.operations:
            count += 1
        counts[job.job_id] = count
    return counts

def order_crossover(parent1, parent2):
    p1_list = list(parent1)
    p2_list = list(parent2)
    tools.cxOrdered(p1_list, p2_list)
    #max_count = 10  # Each value must appear 10 times
    # Repair children 
    p1_list[:] = repair_child(p1_list) 
    p2_list[:] = repair_child(p2_list)
    return p1_list, p2_list


def cycle_crossover(parent1, parent2):
    child1, child2 = [None] * len(parent1), [None] * len(parent2)
    visited = [False] * len(parent1)

    cycle_start = 0
    while not all(visited):  
        if visited[cycle_start]:
            cycle_start = visited.index(False)  

        index = cycle_start
        while not visited[index]:
            visited[index] = True
            child1[index] = parent1[index]
            child2[index] = parent2[index]
            index = parent1.index(parent2[index])

    child1 = [p2 if c1 is None else c1 for c1, p2 in zip(child1, parent2)]
    child2 = [p1 if c2 is None else c2 for c2, p1 in zip(child2, parent1)]

    if None in child1 or None in child2:
        raise ValueError(f"Cycle crossover produced invalid offspring: {child1}, {child2}")

    return child1, child2



def mutate_scramble(individual, indpb):
    if random.random() < indpb:
        start, end = sorted(random.sample(range(len(individual)), 2))
        individual[start:end] = random.sample(individual[start:end], len(individual[start:end]))
    return individual

def mutate_inversion(individual, indpb):
    if random.random() < indpb:
        start, end = sorted(random.sample(range(len(individual)), 2))
        individual[start:end] = individual[start:end][::-1]
    return individual
