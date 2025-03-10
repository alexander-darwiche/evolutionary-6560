import random

from plotting.drawer import plot_gantt_chart, draw_precedence_relations
from data_parsers.parser_fjsp import parse_fjsp
from scheduling_environment.jobShop import JobShop

from solution_methods.helper_functions import load_job_shop_env, load_parameters
from solution_methods.GA.src.initialization import initialize_run
from solution_methods.GA.run_GA import run_GA

jobShopEnv = JobShop()
parameters = load_parameters("configs/GA.toml")
jobShopEnv = load_job_shop_env(parameters['instance'].get('problem_instance'))

jobShopEnv.update_operations_available_for_scheduling()
while len(jobShopEnv.operations_to_be_scheduled) > 0:
    # import pdb;pdb.set_trace()
    operation = random.choice(jobShopEnv.operations_available_for_scheduling)
    machine_id = random.choice(list(operation.processing_times.keys()))
    duration = operation.processing_times[machine_id]
    jobShopEnv.schedule_operation_on_machine(operation, machine_id, duration)
    jobShopEnv.update_operations_available_for_scheduling()

print('Makespan:', jobShopEnv.makespan)

plot = plot_gantt_chart(jobShopEnv)
plot.show()


parameters = load_parameters("configs/GA.toml")
jobShopEnv = load_job_shop_env(parameters['instance'].get('problem_instance'))

# import pdb;pdb.set_trace()
population, toolbox, stats, hof = initialize_run(jobShopEnv, **parameters)
makespan, jobShopEnv = run_GA(jobShopEnv, population, toolbox, stats, hof, **parameters)

plot = plot_gantt_chart(jobShopEnv)
plot.show()

plot = draw_precedence_relations(jobShopEnv)
plot.show()