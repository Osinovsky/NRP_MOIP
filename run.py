# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

# from src import Controller
from src import Analyzer

# Controller.run('binary_nsgaii_test.json')

sheet = Analyzer('classic_nsga').make_sheet()
Analyzer.tabulate('tmp1.csv', sheet)
