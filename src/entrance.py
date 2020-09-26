# Here is the sample on how to use this lib

from runner import Runner
from analyzer import Comparator
from config import *

# main function
if __name__ == '__main__':
    # run all classic and realistic nrps in single form and epsilon

    # config
    out_path = '../result_binary_compare'
    ite_num = 1

    configs = []
    # single
    # for project, file_name in ALL_FILES_DICT.items():
    #     if project.startswith('classic'):
    #         configs.append((project, 'single', 'single', {'b':0.3}))
    #         configs.append((project, 'single', 'single', {'b':0.5}))
    #         configs.append((project, 'single', 'single', {'b':0.7}))
    #     elif project.startswith('realistic'):
    #         configs.append((project, 'single', 'single', {'b':0.3}))
    #         configs.append((project, 'single', 'single', {'b':0.5}))
    # binary, epsilon constraint
    for project, file_name in ALL_FILES_DICT.items():
        if project.startswith('classic') or project.startswith('realistic'):
            configs.append((project, 'binary', 'epsilon'))
            # configs.append((project, 'binary', 'cwmoip'))
            configs.append((project, 'binary', 'ncgop'))
    # prepare names
    names = []
    for config in configs:
        name = Runner.name(*config)
        names.append(name)
        print(name)
    # run
    runner = Runner(configs, out_path, ite_num)

    # compare
    comparator = Comparator(out_path, names, ite_num)
    comparison = comparator.get_content()
    for name in names:
        print(name + '\t\t' + str(comparison[name]['all']['solution number']) \
            + '\t\t' + str(comparison[name]['all']['nd']) \
            + '\t\t' + str(comparison[name]['all']['hv']))