# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

from src import Controller
from src import Analyzer, Result

Controller.run('binary_moea/realistic_moea.json')

# Result.quick_prob('triurgency_exact')

sheet = Analyzer('realistic_binary_moea').make_sheet()
Analyzer.tabulate('realistic_binary_moea.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
