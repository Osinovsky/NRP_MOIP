# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

from src import Controller
# from src import Analyzer
# from src import Comparator

Controller.run('rm3.json')

# Controller.run('bincst_min_profit.json')
# Controller.run('bincst_max_cost.json')
# Controller.run('bincst_min_requirements.json')
# Controller.run('bincst_min_customers.json')

# Comparator('xuan_binary').quick_compare()

# sheet = Analyzer('xuan_binary_nsga').make_sheet()
# Analyzer.tabulate('tmp1.csv', sheet)
