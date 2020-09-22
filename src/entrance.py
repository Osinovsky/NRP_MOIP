# Here is the sample on how to use this lib

from runner import Runner
from config import *

# main function
if __name__ == '__main__':
    # run all classic and realistic nrps in single form and epsilon
    configs = []
    # single
    for project, file_name in ALL_FILES_DICT.items():
        if project.startswith('classic'):
            configs.append((project, 'single', 'single', {'b':0.3}))
            configs.append((project, 'single', 'single', {'b':0.5}))
            configs.append((project, 'single', 'single', {'b':0.7}))
        elif project.startswith('realistic'):
            configs.append((project, 'single', 'single', {'b':0.3}))
            configs.append((project, 'single', 'single', {'b':0.5}))
    # binary, epsilon constraint
    for project, file_name in ALL_FILES_DICT.items():
        if project.startswith('classic') or project.startswith('realistic'):
            configs.append((project, 'binary', 'epsilon'))
    # run
    runner = Runner(configs, RESULT_PATH)