# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.09.08    #
# Last Modified: 2020.09.08          #
# ################################## #

from typing import *
from os import path

from config import *
from loaders import XuanLoader
from naiveSol import NaiveSol
from moipSol import BaseSol
from util import NextReleaseProblem
from dimacsMoipProb import DimacsMOIPProblem 

# construct a wrapper of everything, and name it as runner
class Runner:
    # initialize
    def __init__(self, project_name : str, options : Dict[str, Any]):
        # project file(name)
        if project_name in ALL_FILES_DICT:
            self.__project : str = project_name
        else:
            print("FATAL: cannot load project with name: " + project_name)
            print('maybe you can check out them: ')
            for project in ALL_FILES_DICT.keys():
                print(project)
        # define a loader, could be any type in loaders
        self.__loader = None
        # define the NRP
        self.__NRP = None
        # define the problem (for input in solver)
        self.__problem = None
        # options
        self.__options = options
        # define a solver
        self.__solver = None
    
    # classic loader script
    def __classic_load(self) -> None:
        #  employe a XuanLoader
        self.__loader = XuanLoader()
        self.__loader.load(ALL_FILES_DICT[self.__project])
        # load into NRP
        self.__NRP = NextReleaseProblem()
        self.__NRP.construct_from_XuanLoader(self.__loader)
        # flatten to eliminate all dependencies
        self.__NRP.flatten()
        # reencode the NRP
        self.__NRP.unique_and_compact_reenconde(True)
        # convert to MOIPProblem
        assert 'b' in self.__options
        self.__problem = self.__NRP.to_general_form(self.__options['b'])
    
    # realistic loader script
    def __realistic_load(self) -> None:
        #  employe a XuanLoader
        self.__loader = XuanLoader()
        self.__loader.load(ALL_FILES_DICT[self.__project])
        # load into NRP
        self.__NRP = NextReleaseProblem()
        self.__NRP.construct_from_XuanLoader(self.__loader)
        # there shouldn't be any dependencies in NRP
        assert self.__NRP.empty_denpendencies()
        # reencode the NRP
        self.__NRP.unique_and_compact_reenconde(True)
        # convert to MOIPProblem
        assert 'b' in self.__options
        self.__problem = self.__NRP.to_basic_stakeholder_form(self.__options['b'])

    # choose a loader from the project name
    # and load it into NRP and convert to MOIPProblem
    def __load(self) -> None:
        # check first
        assert self.__project in ALL_FILES_DICT
        # prepare loader
        if self.__project.startswith('classic_'):
            self.__classic_load()
        elif self.__project.startswith('realistic_'):
            self.__realistic_load()
    
    # save result into file, choosing by the project name
    def __save(self) -> None:
        # make result path
        file_path = path.join(RESULT_PATH, self.__project)
        # make file name
        file_name = path.join(file_path, 'Pareto.txt')
        # save to file 
        self.__solver.outputCplexParetoMap(file_name)

    # display the solutions
    def __display(self) -> None:
        for solution in self.__solver.cplexParetoSet:
            print(str(solution) + ', ')

    # classic nrp runner
    def __classic_runner(self) -> None:
        # load the project file
        # At first, get the file name
        assert self.__project in ALL_FILES_DICT
        # then load: file -> loader -> NRP -> MOIPProblem
        self.__load()
        # use base sol
        self.__solver = BaseSol(self.__problem)
        # prepare and execute
        self.__solver.prepare()
        self.__solver.execute()
        # self.__save()
        self.__display()

    # realistic nrp runner
    def __realistic_runner(self) -> None:
        # load the project file
        # At first, get the file name
        assert self.__project in ALL_FILES_DICT
        # then load: file -> loader -> NRP -> MOIPProblem
        self.__load()
        # use base sol
        self.__solver = BaseSol(self.__problem)
        # prepare and execute
        self.__solver.prepare()
        self.__solver.execute()
        # self.__save()
        self.__display()

    # run! no bullshit just run
    def run(self) -> None:
        # branch runner
        if self.__project.startswith('classic_'):
            self.__classic_runner()
        elif self.__project.startswith('realistic_'):
            self.__realistic_runner()


# main function
if __name__ == '__main__':
    for project in ALL_FILES_DICT.keys():
        if project.startswith('classic_'):
            for b in [0.3, 0.5, 0.7]:
                print(project + '\t' + str(b))
                runner = Runner(project, {'b':b})
                runner.run()
        elif project.startswith('realistic_'):
            for b in [0.3, 0.5]:
                print(project + '\t' + str(b))
                runner = Runner(project, {'b':b})
                runner.run()
