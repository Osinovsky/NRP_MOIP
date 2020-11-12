# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

# from src import Controller
from src import Analyzer

# Controller.run('binary_test.json')

# Analyzer('xuan_binary_test').plot_2D_pareto('classic_1')
sheet = Analyzer('xuan_binary_test').make_sheet(tab_iteration=False)
Analyzer.tabulate('tmp.csv', sheet)
