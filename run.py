# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller
from src import Analyzer, Result

folder = ''
Controller.run('moea' + folder + '.json')

gc.collect()

analyzer = Analyzer(folder)
sheet = analyzer.make_better_sheet(methods=['epsilon', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
# sheet = analyzer.make_better_sheet(methods=['normal', 'NSGAII', 'IBEA'], indicators=['igd', 'hv', 'evenness'])
Analyzer.tabulate(folder + '.csv', sheet)
# analyzer.plot_2D_pareto('classic_1')

# Result.quick_prob('triurgency_exact')

# sheet = Analyzer('realistic_binary_moea').make_sheet()
# Analyzer.tabulate('realistic_binary_moea.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
