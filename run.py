# HERE IS ON HOW TO LOAD TASKS AND RUN THEM

import gc
from src import Controller

Controller.run('template.json')

gc.collect()
