# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# runner.py, created: 2020.09.22     #
# Last Modified: 2020.10.28          #
# ################################## #

from typing import *
import time
import os
import json
from NRP import NextReleaseProblem, ProblemType
from solvers import Solver
from config import *

# config type
ConfigType = Dict[str, Any]

# construct a wrapper of everything, and name it as runner
# NOTE: config should contain ite_num, project_num, form, method and option
class Runner:
    # initialize
    def __init__(self, configs : List[ConfigType], out_path : str):
        # not changed member
        self.__result = dict()
        # prepare const members
        # jmetal solvers
        self.jmetal_solvers = MOEA_METHOD
        # prepare members
        self.__project : str = None
        self.__method : str = None
        self.__form : str = None
        self.__nrp : NextReleaseProblem = None
        self.__problem : ProblemType = None
        self.__solver : Solver = None
        self.__solutions : Set[Any] = None
        # config should be a list
        assert isinstance(configs, list)
        # check out_path if exists
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # run the configurations
        for one_config in configs:
            # get the ite_num from config
            ite_num = one_config['ite_num']
            del one_config['ite_num']
            assert ite_num > 0
            # config name
            config_name = self.name(**one_config)
            print(config_name + ' will run ' + str(ite_num) + ' times')
            # check the config
            if not self.check_config(**one_config):
                print('FATAL: illegal config input ' + config_name)
                continue
            # each config run ite_num times
            for ind in range(ite_num):
                # run this config
                print('round: ', ind)
                self.run_once(one_config, config_name, ind)
                # dump solutions each round
                self.dump_once(out_path, config_name, ind)
            # print out message that each round has ended
            print('\r\t\t\t\t\t\t\t\t\t\t\t\t\r' + config_name + ' finished')
        # dump result
        self.dump(out_path, ite_num, False)

    # check config
    def check_config(self, project_name : str, form : str, method : str, option : Dict[str, Any] = None) -> bool:
        check = True
        # check config
        if project_name not in ALL_FILES_DICT:
            check = False
        if form not in NRP_FORMS:
            check = False
        if method not in SOLVING_METHOD:
            check = False
        # prepare message
        message = 'config: project:' + project_name + ' form: ' + form + ' method: ' + method
        if option:
            message += ' option: ' + str(option)
        if not check:
            # print out
            print(message, ' fail')
            return False
        else:
            print(message, ' start')
            return True

    # clear
    def clear(self) -> None:
        self.__project = None
        self.__method = None
        self.__form = None
        self.__nrp = None
        self.__problem = None
        self.__solver = None
        self.__solutions = None

    # run once
    def run_once(self, config : ConfigType, name : str, ind : int) -> None: 
        # this config name
        # print('\r\t\t\t\t\t\t\t\t\t\t\t\t\r' + name + ' round: ' + str(ind), end='')
        print(name + ' round: ' + str(ind))
        # clear all members
        self.clear()
        # prepare_config
        self.prepare_once(**config)
        # run
        elapsed_time = self.run()
        # collect results
        self.__solutions = self.__solver.solutions()
        if ind == 0:
            # first round, initialize
            self.__result[name] = dict()
        # record
        self.__result[name][str(ind)] = dict()
        self.__result[name][str(ind)]['runtime'] = elapsed_time
        self.__result[name][str(ind)]['solution number'] = len(self.__solutions)
        self.__result[name][str(ind)]['solutions'] = self.__solutions
        # just for debug
        # self.__result[name][str(ind)]  = dict()
        # self.__result[name][str(ind)] ['runtime'] = 3.33
        # self.__result[name][str(ind)] ['solution number'] = 100
        # self.__result[name][str(ind)] ['solutions'] = set([(1,2), (3,4), (5,6), (7,8), (9,0)])

    # prepare once
    def prepare_once(self, project_name : str, form : str, method : str, option : Dict[str, Any] = None) -> None:
        self.__project = project_name
        self.__method = method
        self.__form = form
        if method in self.jmetal_solvers:
            type = 'jmetal'
            # dump config in /dump/ folder
            Runner.dump_config(project_name, form, option)
        else:
            type = 'default'
        self.__nrp = NextReleaseProblem(project_name, type)
        self.__problem = self.__nrp.model(form, option)
        self.__solver = Solver(method, option)
        self.__solver.load(self.__problem)
        # empty solutions
        self.__solutions = None

    # dump solutions once
    def dump_once(self, out_path : str, name : str, ind : int):
        # exact output path
        exact_path = os.path.join(out_path, name)
        # check if result folder exists
        if not os.path.exists(exact_path):
            os.makedirs(exact_path)
        # prepare the solution file
        file_name = os.path.join(exact_path, str(ind)+'.txt')
        assert name in self.__result
        assert str(ind) in self.__result[name]
        assert 'solutions' in self.__result[name][str(ind)]
        # write to file
        with open(file_name, 'w') as file_out:
            for solution in list(self.__result[name][str(ind)]['solutions']):
                file_out.write(str(solution)+'\n')
        # delete it in checklist for saving memory
        del self.__result[name][str(ind)]['solutions']
        # write a runtime info. file
        file_name = os.path.join(exact_path, 'info_'+str(ind)+'.json')
        with open(file_name, 'w') as info_file:
            json_object = json.dumps(self.__result[name][str(ind)], indent = 4)
            info_file.write(json_object)
            info_file.close()
    
    # run! just run!
    def run(self) -> float:
        start = time.clock()
        self.__solver.execute()
        end = time.clock()
        return end - start

    # display solutions
    def display(self, mode : bool = False) -> None:
        # print solution number found
        print('number of solutions found: ' + str(len(self.__solutions)))
        if not mode:
            return
        # print each solution
        for solution in self.__solutions:
            print(str(solution) + ', ')
    
    # dump jmetal config
    @staticmethod
    def dump_config(project_name : str, form : str, option : Dict[str, Any]) -> None:
        # prepare the new option dict
        neo_option = dict()
        for key, value in option.items():
            if not value:
                # None
                neo_option[key] = 'n'
            elif isinstance(value, int):
                # int
                neo_option[key] = 'i' + str(value)
            elif isinstance(value, float):
                # float
                neo_option[key] = 'f' + str(value)
            else:
                assert False
        # end for
        json_object = json.dumps(neo_option, indent=4)
        # create DUMP PATH if not exists
        if not os.path.exists(os.path.dirname(DUMP_PATH)):
            os.makedirs(DUMP_PATH)
        # prepare file name
        file_name = os.path.join(DUMP_PATH, ('config_' + project_name + '_' + form + '.json'))
        # create config file
        with open(file_name, 'w+') as file_out:
            file_out.write(json_object)
            file_out.close()
        # end with

    # config name
    @staticmethod
    def name(project_name : str, form : str, method : str, option : Dict[str, Any] = None) -> str:
        name_str = project_name + '_' + form + '_' + method
        option_str = ''
        if option:
            for k, v in option.items():
                option_str += '_' + str(k) + str(v)
        return name_str + option_str

    # parse name to config
    # Note that if there are options, it will just return the string
    # because we cannot know it's structure here
    @staticmethod
    def dename(name : str) -> None:
        # name should be a string
        assert isinstance(name, str)
        # parse the project name first
        project_name = None
        for project in ALL_FILES_DICT:
            if name.startswith(project):
                project_name = project
                name = name[len(project)+1:]
        assert project_name
        # split by '_'
        args = name.split('_')
        assert len(args) >= 2
        # note that if length == 2, [2:] will be an empty list
        return {'project' : project_name, 'form' : args[0], 'method' : args[1], 'option' : args[2:]}

    # dump all solutions
    def dump(self, out_path : str, ite_num : int, write_solutions : bool = False) -> None:
        # result folder should already there
        assert os.path.exists(os.path.dirname(out_path))
        # wirte solution if mode is True
        if write_solutions:
            for name, content in self.__result.items():
                # prepare each result folder
                exact_path = os.path.join(out_path, name)
                os.makedirs(exact_path, exist_ok=True)
                for ind in range(ite_num):
                    # simple check
                    assert ind in content
                    assert 'solutions' in content[ind]
                    # prepare file
                    solution_file = open(os.path.join(exact_path, str(ind)+'.txt'), "w+")
                    # write into file
                    for solution in list(content[str(ind)]['solutions']):
                        solution_file.write(str(solution) + '\n')
                    solution_file.close()
                    del content[str(ind)]['solutions']
        # write checklist
        checklist_file = open(os.path.join(out_path, 'checklist.json'), 'w+')
        json_object = json.dumps(self.__result, indent = 4)
        checklist_file.write(json_object)
        checklist_file.close()