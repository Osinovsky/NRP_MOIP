# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

from src import Controller
from src import Analyzer, Result

Controller.run('ibea_binary.json')

# Result.quick_prob('rp_bincst')

# sheet = Analyzer('classic_nsga').make_sheet()
# Analyzer.tabulate('tmp1.csv', sheet)
