# Here is the sample on how to use this lib

from runner import Runner
from analyzer import Comparator
from config import *

# main function
if __name__ == '__main__':
    # run all classic and realistic nrps in single form and epsilon

    # config
    out_path = '../result_epsilon_cwmoip'
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
    count = 0
    for project, file_name in ALL_FILES_DICT.items():
        if project.startswith('classic') or project.startswith('realistic'):
            count += 1
            if count == 2:
                configs.append((project, 'binary', 'epsilon'))
                configs.append((project, 'binary', 'cwmoip'))
                # configs.append((project, 'binary', 'ncgop'))
                break
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
    # comparison = comparator.get_content()
    # which_names, which_project = Comparator.parse_names(names)
    # for project, name_list in which_names.items():
    #     for name in name_list:
    #         print(name + '\t\t' + str(comparison[project][name]['all']['solution number']) \
    #             + '\t\t' + str(comparison[project][name]['all']['nd']) \
    #             + '\t\t' + str(comparison[project][name]['all']['hv']))

    # load and display
    comparison = Comparator.load(out_path, 'comparison.json')
    template = '{NAME:32}|{RT:12}|{ND:8}|{IGD:12}|{HV:12}|{E:12}'
    # header
    print(template.format(NAME='Name', RT='Runtime', ND='NonD', IGD='IGD', HV='HV', E='Evenness'))
    for project_name in comparison:
        print('project name: ' + project_name)
        for name, value in comparison[project_name].items():
            print(template.format(
                NAME=name, SN=str(value['all']['solution number']),
                RT=str(round(value['all']['runtime'], 2)),
                ND=str(value['all']['nd']), IGD=str(round(value['all']['igd'], 2)),
                HV=str(round(value['all']['hv'], 3)), E=str(round(value['all']['evenness'], 3))
            ))
    