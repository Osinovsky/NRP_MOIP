# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller
from src import Analyzer, Result

Controller.run('triple.json')

gc.collect()

folder = 'triple'
sheet = Analyzer(folder).make_better_sheet(methods=['nromal', 'NSGAII', 'IBEA'], indicators=['igd', 'hv', 'evenness'])
Analyzer.tabulate(folder + '.csv', sheet)

# Result.quick_prob('triurgency_exact')

# sheet = Analyzer('realistic_binary_moea').make_sheet()
# Analyzer.tabulate('realistic_binary_moea.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
