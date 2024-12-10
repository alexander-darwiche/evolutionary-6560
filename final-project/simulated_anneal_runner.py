import random

from plotting.drawer import plot_gantt_chart, draw_precedence_relations
from data_parsers.parser_fjsp import parse_fjsp
from scheduling_environment.jobShop import JobShop

from solution_methods.helper_functions import load_job_shop_env, load_parameters
from solution_methods.SA.src.initialization import initialize_run
from solution_methods.SA.run_SA import run_SA

jobShopEnv = JobShop()
parameters = load_parameters("configs/SA.toml")
jobShopEnv = load_job_shop_env(parameters['instance'].get('problem_instance'))

choices = list()
# Randomly assign operations to machines
jobShopEnv.update_operations_available_for_scheduling()
while len(jobShopEnv.operations_to_be_scheduled) > 0:
    operation = random.choice(jobShopEnv.operations_available_for_scheduling)
    choices.append(operation.job_id)
    machine_id = random.choice(list(operation.processing_times.keys()))
    duration = operation.processing_times[machine_id]
    jobShopEnv.schedule_operation_on_machine(operation, machine_id, duration)
    jobShopEnv.update_operations_available_for_scheduling()

print(choices)
print(jobShopEnv.makespan)

jobShopEnv.choices = choices

# plot = plot_gantt_chart(jobShopEnv)
# plot.show()

# parameters = load_parameters("configs/SA.toml")
# jobShopEnv = load_job_shop_env(parameters['instance'].get('problem_instance'))

# jobShopEnv = initialize_run(jobShopEnv, **parameters)
makespan, jobShopEnv = run_SA(jobShopEnv, **parameters)

import pdb;pdb.set_trace()
plot = plot_gantt_chart(jobShopEnv)
plot.show()

plot = draw_precedence_relations(jobShopEnv)
plot.show()