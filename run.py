# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller
from src import Analyzer, Result

# Controller.run('./baan/bin_exact.json')
# Controller.run('./baan/moea.json')
Controller.run('tmp.json')

gc.collect()

for folder in ['baan_binary_moea', 'baan_bincst_moea']:
    analyzer = Analyzer(folder)
    sheet = analyzer.make_better_sheet(methods=['imprec', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
    Analyzer.tabulate(folder + '.csv', sheet)

folder = 'baan_triurgency'
sheet = analyzer.make_better_sheet(methods=['normal', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
Analyzer.tabulate(folder + '.csv', sheet)

# Result.quick_prob('triurgency_exact')

# sheet = Analyzer('realistic_binary_moea').make_sheet()
# Analyzer.tabulate('realistic_binary_moea.csv', sheet)
# analyzer = Analyzer('xuan_binary_')
# for index in range(1, 6):
#     project = 'classic_' + str(index)
#     analyzer.plot_2D_pareto(project, [], '' + project)
