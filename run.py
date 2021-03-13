# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller
from src import Analyzer

Controller.run('tmp.json')

gc.collect()

# for folder in ['baan_binary_exact', 'baan_bincst_exact']:
#     analyzer = Analyzer(folder)
#     sheet = analyzer.make_better_sheet(methods=['epsilon', 'imprec', 'cwmoip'], indicators=['igd', 'hv', 'evenness'])
#     Analyzer.tabulate(folder + '.csv', sheet)

# for folder in ['baan_binary_moea', 'baan_bincst_moea']:
#     analyzer = Analyzer(folder)
#     sheet = analyzer.make_better_sheet(methods=['imprec', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
#     Analyzer.tabulate(folder + '.csv', sheet)

folder = 'baan_triurgency'
analyzer = Analyzer(folder)
sheet = analyzer.make_better_sheet(methods=['normal', 'NSGAII'], indicators=['igd', 'hv', 'evenness'])
Analyzer.tabulate(folder + '.csv', sheet)
