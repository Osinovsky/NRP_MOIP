# Here is the sample on how to use this lib

from runner import Runner
from analyzer import Comparator
from config import *
from copy import deepcopy

# make config(dict)
def make_config(project_name, form, method, ite_num=1, option = None):
    the_config = dict()
    the_config['project_name'] = project_name
    the_config['form'] = form
    the_config['method'] = method
    the_config['ite_num'] = ite_num
    the_config['option'] = option
    return the_config

# remove ite_num
def pure_config(the_config):
    konfig = deepcopy(the_config)
    del konfig['ite_num']
    return konfig

# run bicst config
def bicst_run(option, out_path):
    configs = []
    for project, file_name in ALL_FILES_DICT.items():
        if project.startswith('classic'): #  or project.startswith('realistic')
            configs.append(make_config(project, 'bicst', 'cwmoip', 1, option))
            configs.append(make_config(project, 'bicst', 'epsilon', 1, option))
    # names = []
    # for one_config in configs:
    #     name = Runner.name(**pure_config(one_config))
    #     names.append(name)
    #     print(name)
    #run
    runner = Runner(configs, out_path)

# main function
if __name__ == '__main__':
    # option
    # option = {'max_cost' : None, 'min_profit' : None, 'min_requirements' : None, 'min_customers' : None}

    # interval
    # interval = [0.7, 0.5, 0.3]
    # max cost
    # for rhs in interval:
    #     print('max cost: ', rhs)
    #     option = {'max_cost' : rhs, 'min_profit' : None, 'min_requirements' : None, 'min_customers' : None}
    #     bicst_run(option, '../result_max_cost'+str(rhs))
    # min profit
    # for rhs in interval:
    #     print('min profit: ', rhs)
    #     option = {'max_cost' : None, 'min_profit' : rhs, 'min_requirements' : None, 'min_customers' : None}
    #     bicst_run(option, '../result_min_profit'+str(rhs))
    # min requirements
    # for rhs in interval:
    #     print('min requirements: ', rhs)
    #     option = {'max_cost' : None, 'min_profit' : None, 'min_requirements' : rhs, 'min_customers' : None}
    #     bicst_run(option, '../result_min_req'+str(rhs))
    # min customers
    # for rhs in interval:
    #     print('min customers: ', rhs)
    #     option = {'max_cost' : None, 'min_profit' : None, 'min_requirements' : None, 'min_customers' : rhs}
    #     bicst_run(option, '../result_min_cus'+str(rhs))

    ###############################################################

    # run all classic and realistic nrps in single form and epsilon

    # config
    out_path = '../result_20201027'
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
            if count == 1:
                option = {'max_cost' : None, 'min_profit' : None, 'min_requirements' : None, 'min_customers' : None} 
                # configs.append(make_config(project, 'bicst', 'cwmoip', 1, option))
                # configs.append(make_config(project, 'bicst', 'epsilon', 1, option))
                # configs.append(make_config(project, 'trireq', 'cwmoip'))
                # configs.append(make_config(project, 'trireq', 'epsilon'))
                # configs.append(make_config(project, 'binary', 'ncgop'))
                configs.append(make_config(project, 'binary', 'NSGAII', 1, {'mutation': 0.035, 'crossover':1.0, 'max_evaluation' : MAX_EVALUATION, 'tolerance':10}))
                # configs.append(make_config(project, 'binary', 'HYPE'))

    # prepare names
    # names = []
    # for one_config in configs:
    #     name = Runner.name(**pure_config(one_config))
    #     names.append(name)
    #     print(name)
    # run
    runner = Runner(configs, out_path)

    # compare
    # comparator = Comparator(out_path, names, ite_num)

    # load and display
    # comparison = Comparator.load(out_path, 'comparison.json')
    # template = '{NAME:32}|{RT:12}|{ND:8}|{IGD:12}|{HV:12}|{E:12}'
    # header
    # print(template.format(NAME='Name', RT='Runtime', ND='NonD', IGD='IGD', HV='HV', E='Evenness'))
    # for project_name in comparison:
    #     print('project name: ' + project_name)
    #     for name, value in comparison[project_name].items():
    #         print(template.format(
    #             NAME=name, SN=str(value['all']['solution number']),
    #             RT=str(round(value['all']['runtime'], 2)),
    #             ND=str(value['all']['nd']), IGD=str(round(value['all']['igd'], 2)),
    #             HV=str(round(value['all']['hv'], 3)), E=str(round(value['all']['evenness'], 3))
    #         ))
    