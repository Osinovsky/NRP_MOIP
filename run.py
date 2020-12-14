# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

from src import Controller
# from src import Analyzer
# from src import Comparator

Controller.run('binary_nsgaii_test.json')

# Comparator('xuan_binary').quick_compare()

# sheet = Analyzer('xuan_binary_nsga').make_sheet()
# Analyzer.tabulate('tmp1.csv', sheet)
