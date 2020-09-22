# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# runner.py, created: 2020.09.22     #
# Last Modified: 2020.09.22          #
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
    def __init__(self, config : Union[ConfigType, List[ConfigType]], out_path : str):
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
        # config just one
        if isinstance(config, tuple):
            config = [config]
        if isinstance(config, list):
            # run
            for one_config in config:
                # run this config
                self.run_once(one_config, self.name(*one_config))
            # dump result
            self.dump(out_path)
        else:
            print('FATAL: illegal config input')

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
            print(message)
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
    def run_once(self, config : ConfigType, name : str) -> None: 
        # this config name
        print(name)
        if not self.check_config(*config):
            return
        # clear all members
        self.clear()
        # prepare_config
        self.prepare_once(*config)
        # run
        elapsed_time = self.run()
        # collect results
        self.__result[name] = dict()
        self.__result[name]['runtime'] = elapsed_time
        self.__result[name]['solution number'] = len(self.__solutions)
        self.__result[name]['solutions'] = self.__solutions
        # just for debug
        # self.__result[name] = dict()
        # self.__result[name]['runtime'] = 3.33
        # self.__result[name]['solution number'] = 100
        # self.__result[name]['solutions'] = set([(1,2), (3,4), (5,6), (7,8), (9,0)])

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

    # dump solutions
    def dump(self, out_path : str) -> None:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # wirte solution
        for name, content in self.__result.items():
            solution_file = open(os.path.join(out_path, name+'.txt'), "w+")
            for solution in list(content['solutions']):
                solution_file.write(str(solution) + '\n')
            solution_file.close()
            del content['solutions']
        # write checklist
        checklist_file = open(os.path.join(out_path, 'checklist.json'), 'w+')
        json_object = json.dumps(self.__result, indent = 4)
        checklist_file.write(json_object)
        checklist_file.close()