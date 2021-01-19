# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller
from src import Analyzer, Result

# Controller.run('c_binary.json')
# Controller.run('c_bincst.json')
# Controller.run('e_binary.json')
# Controller.run('e_binary.json')

gc.collect()

folder = 'tmp'
sheet = Analyzer(folder).make_better_sheet(methods=['epsilon', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
Analyzer.tabulate(folder + '.csv', sheet)

# Result.quick_prob('triurgency_exact')

# sheet = Analyzer('realistic_binary_moea').make_sheet()
# Analyzer.tabulate('realistic_binary_moea.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
