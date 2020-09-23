# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# runner.py, created: 2020.09.22     #
# Last Modified: 2020.09.23          #
# ################################## #

from typing import *
import time
import os
import json
from NRP import NextReleaseProblem
from moipProb import MOIPProblem
from solvers import Solver
from config import *

# config type
ConfigType = Tuple[str, str, str, Dict[str, Any]]

# construct a wrapper of everything, and name it as runner
class Runner:
    # initialize
    def __init__(self, configs : List[ConfigType], out_path : str, ite_num : str = 1):
        # not changed member
        self.__result = dict()
        # prepare members
        self.__project : str = None
        self.__method : str = None
        self.__form : str = None
        self.__nrp : NextReleaseProblem = None
        self.__problem : MOIPProblem = None
        self.__solver : Solver = None
        self.__solutions : Set[Any] = None
        # config should be a list
        assert isinstance(configs, list)
        # and ite times should be positive
        assert ite_num > 0
        print('All job will run ' + str(ite_num) + ' times')
        # check out_path if exists
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # run the configurations
        for one_config in configs:
            # config name
            config_name = self.name(*one_config)
            # check the config
            if not self.check_config(*one_config):
                print('FATAL: illegal config input ' + config_name)
                continue
            # each config run ite_num times
            for ind in range(ite_num):
                # run this config
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
        print('\r\t\t\t\t\t\t\t\t\t\t\t\t\r' + name + ' round: ' + str(ind), end='')
        # clear all members
        self.clear()
        # prepare_config
        self.prepare_once(*config)
        # run
        # elapsed_time = self.run()
        # collect results
        if ind == 0:
            # first round, initialize
            self.__result[name] = dict()
        # record
        # self.__result[name][ind] = dict()
        # self.__result[name][ind]['runtime'] = elapsed_time
        # self.__result[name][ind]['solution number'] = len(self.__solutions)
        # self.__result[name][ind]['solutions'] = self.__solutions
        # just for debug
        self.__result[name][ind]  = dict()
        self.__result[name][ind] ['runtime'] = 3.33
        self.__result[name][ind] ['solution number'] = 100
        self.__result[name][ind] ['solutions'] = set([(1,2), (3,4), (5,6), (7,8), (9,0)])

    # prepare once
    def prepare_once(self, project_name : str, form : str, method : str, option : Dict[str, Any] = None) -> None:
        self.__project = project_name
        self.__method = method
        self.__form = form
        self.__nrp = NextReleaseProblem(project_name)
        self.__problem = self.__nrp.model(form, option)
        self.__solver = Solver(method)
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
        assert ind in self.__result[name]
        assert 'solutions' in self.__result[name][ind]
        # write to file
        with open(file_name, 'w') as file_out:
            for solution in list(self.__result[name][ind]['solutions']):
                file_out.write(str(solution)+'\n')
        # delete it in checklist for saving memory
        del self.__result[name][ind]['solutions']
    
    # run! just run!
    def run(self) -> float:
        start = time.clock()
        self.__solutions = self.__solver.execute()
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

    # config name
    @staticmethod
    def name(project_name : str, form : str, method : str, option : Dict[str, Any] = None) -> str:
        name_str = project_name + '_' + form + '_' + method
        option_str = ''
        if option:
            for k, v in option.items():
                option_str += '_' + str(k) + str(v)
        return name_str + option_str

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
                    for solution in list(content[ind]['solutions']):
                        solution_file.write(str(solution) + '\n')
                    solution_file.close()
                    del content[ind]['solutions']
        # write checklist
        checklist_file = open(os.path.join(out_path, 'checklist.json'), 'w+')
        json_object = json.dumps(self.__result, indent = 4)
        checklist_file.write(json_object)
        checklist_file.close()