# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# runner.py, created: 2020.09.22     #
# Last Modified: 2020.09.22          #
# ################################## #

from typing import *
from NRP import NextReleaseProblem
from solvers import Solver
from config import *

# construct a wrapper of everything, and name it as runner
class Runner:
    # initialize
    def __init__(self, \
        project_name : str, \
        form : str, \
        method : str, \
        option : Dict[str, Any] = None, \
    ):
        # project file(name)
        if project_name in ALL_FILES_DICT:
            self.__project : str = project_name
        else:
            print("FATAL: cannot load project with name: " + project_name)
            print('maybe you can check out them: ')
            for _project_name in ALL_FILES_DICT.keys():
                print(_project_name)
        # method
        if method in SOLVING_METHOD:
            self.__method = method
        else:
            print("FATAL: illegal : " + project_name)
            print('please select one from list below: ')
            for method_name in SOLVING_METHOD:
                print(method_name)
        # employ NRP, Solver
        self.__nrp = NextReleaseProblem(project_name)
        self.__problem = self.__nrp.model(form, option)
        self.__solver = Solver(method)
        self.__solver.load(self.__problem)
        # empty solutions
        self.__solutions = None
    
    # run! just run!
    def run(self) -> None:
        self.__solutions = self.__solver.execute()

    # display solutions
    def display(self, mode : bool = False) -> None:
        # print solution number found
        print('number of solutions found: ' + str(len(self.__solutions)))
        if not mode:
            return
        # print each solution
        for solution in self.__solutions:
            print(str(solution) + ', ')