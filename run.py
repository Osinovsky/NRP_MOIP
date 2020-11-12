# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

# from src import Controller
from src import Analyzer

# Controller.run('binary_test.json')

sheet = Analyzer('xuan_binary_test').make_sheet(tab_iteration=True)
Analyzer.tabulate('tmp1.csv', sheet)

sheet = Analyzer('xuan_binary_test').make_sheet(tab_iteration=True)
Analyzer.tabulate('tmp2.csv', sheet)
