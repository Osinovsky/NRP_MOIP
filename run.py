# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

from src import Controller
from src import Analyzer, Result

Controller.run('binary/rp.json')

# Result.quick_prob('triurgency_exact')

# sheet = Analyzer('classic_nsga').make_sheet()
# Analyzer.tabulate('tmp1.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
