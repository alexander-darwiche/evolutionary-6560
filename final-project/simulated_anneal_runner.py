import random

from plotting.drawer import plot_gantt_chart, draw_precedence_relations
from data_parsers.parser_fjsp import parse_fjsp
from scheduling_environment.jobShop import JobShop

from solution_methods.helper_functions import load_job_shop_env, load_parameters
from solution_methods.SA.src.initialization import initialize_run
from solution_methods.SA.run_SA import run_SA
from solution_methods.SA.src.heuristics import global_load_balancing_scheduler_SA, global_load_balancing_scheduler

jobShopEnv = JobShop()
parameters = load_parameters("configs/SA.toml")
jobShopEnv = load_job_shop_env(parameters['instance'].get('problem_instance'))

choices = list()
machine_choices = list()

# Solve initial solution
jobShopEnv = global_load_balancing_scheduler_SA(jobShopEnv)

# Run Simulated Annealing
jobShopEnv = run_SA(jobShopEnv, **parameters)

# Plot
plot = plot_gantt_chart(jobShopEnv)
plot.show()

plot = draw_precedence_relations(jobShopEnv)
plot.show()