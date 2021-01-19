#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Controller.py, created: 2020.11.02
# last modified: 2021.01.14
#

import json
import gc
from time import clock
from copy import deepcopy
from typing import Dict, Any, List, Union, Tuple, Set
from os import makedirs
from os.path import isdir, join, abspath
from src.Config import Config
from src.NRP import NextReleaseProblem
from src.Solver import Solver

# type
Entry = Tuple[str, Dict[str, Any]]


class Task:
    def __init__(self,
                 root_folder: str,
                 problem: str,
                 modelling: Entry,
                 method: Entry
                 ) -> None:
        """__init__ [summary] define members
        """
        self.root_folder: str = root_folder
        self.problem: str = problem
        self.modelling: Entry = modelling
        self.method: Entry = method

    def __str__(self) -> str:
        dict_object: Dict[str, Any] = {}
        dict_object['root_folder'] = self.root_folder
        dict_object['problem'] = self.problem
        dict_object['modelling'] = {
            'name': self.modelling[0],
            'option': self.modelling[1]
        }
        dict_object['method'] = {
            'name': self.method[0],
            'option': self.method[1]
        }
        return json.dumps(dict_object, indent=2)


class Controller:
    def __init__(self) -> None:
        """__init__ [summary] define members
        """
        pass

    @staticmethod
    def load_json(json_file: str) -> Dict[str, Any]:
        """load_json [summary] load json file

        Args:
            json_file (str): [description] *.json file name

        Returns:
            Dict[str, Any]: [description] return the dict content in that file
        """
        data = None
        with open(json_file, 'r') as fin:
            data = json.load(fin)
            fin.close()
        return data

    @staticmethod
    def parse_tasks(
                    tasks: Union[List[Dict[str, Any]], Dict[str, Any]]
                    ) -> List[Task]:
        """parse_tasks [summary] parse all tasks

        Args:
            tasks (Union[List[Dict[str, Any]], Dict[str, Any]]):
            [description] raw tasks

        Returns:
            List[Task]: [description] return the task that could run
        """
        # prepare task list
        task_list: List[Task] = []
        # check tasks is a array or a json dict
        if isinstance(tasks, dict):
            # turn into (json)array (python list)
            tasks = [tasks]
        # parse each task
        for task in tasks:
            task_list += Controller.parse_task(task)
        # return
        return task_list

    @staticmethod
    def parse_task(task: Dict[str, Any]) -> List[Task]:
        """parse_task [summary] parse raw task into runnable task list

        Args:
            task (Dict[str, Any]):
            [description] raw task

        Returns:
            List[Task]: [description] runnable taks list
        """
        # load config
        config = Config()
        # find the task name
        assert 'name' in task
        task_name: str = task['name']

        # parse the datasets
        assert 'dataset' in task
        dataset = task['dataset']
        # gather all problems it needs
        problems: Set[str] = set()
        problems_list: List[str] = []
        if isinstance(dataset, str):
            dataset = [dataset]
        for name in dataset:
            type = config.name_type(name)
            if type == 'problem':
                if name not in problems:
                    problems.add(name)
                    problems_list.append(name)
            elif type == 'keyword':
                cluster = set(config.keyword_cluster(name))
                for set_name in cluster:
                    if set_name not in problems:
                        problems.add(set_name)
                        problems_list.append(set_name)
            elif type == 'dataset':
                cluster = set(config.dataset_cluster(name))
                for set_name in cluster:
                    if set_name not in problems:
                        problems.add(set_name)
                        problems_list.append(set_name)
            else:
                print(name, ' not exists')
        # end for
        # parse the modelling
        assert 'modelling' in task
        formatting = task['modelling']
        modellings: List[Entry] = []
        if isinstance(formatting, dict):
            formatting = [formatting]
        for modelling in formatting:
            assert 'name' in modelling
            modelling_name = modelling['name']
            assert modelling_name in config.modelling
            del modelling['name']
            modellings.append((modelling_name, modelling))
        # end for
        # parse the methods
        assert 'method' in task
        algorithms = task['method']
        methods: List[Entry] = []
        if isinstance(algorithms, dict):
            algorithms = [algorithms]
        for algorithm in algorithms:
            assert 'name' in algorithm
            method_name = algorithm['name']
            assert method_name in config.method
            del algorithm['name']
            methods.append((method_name, algorithm))
        # end for

        # prepare task list
        task_list: List[Task] = []
        # Till here, we got problem_list, methods, modellings
        # Now, make tasks from them
        for problem in sorted(problems_list):  # TODO: better way than sorting?
            for model in modellings:
                for method in methods:
                    # create a task
                    task_list.append(Task(task_name, problem, model, method))
        # end nest for
        return task_list

    @staticmethod
    def project_name(problem: str, modelling: str,
                     modelling_option: Dict[str, Any]) -> str:
        """project_name [summary] make string of a project

        Args:
            problem (str): [description] problem name
            modelling (str): [description] modelling method
            modelling_option (Dict[str, Any]): [description] options

        Returns:
            str: [description] the string (all in one)
        """
        name = problem + '-' + modelling
        option_str = ''
        if modelling_option:
            for key, value in modelling_option.items():
                if value is None:
                    pass
                elif isinstance(value, str):
                    if '/' in value or ':' in value or '\\' in value:
                        pass
                    else:
                        pair_str = '-' + key + '+' + str(value)
                        option_str += pair_str
                else:
                    pair_str = '-' + key + '+' + str(value)
                    option_str += pair_str
        # end if
        return name + option_str

    @staticmethod
    def method_name(method: str, method_option: Dict[str, Any]) -> str:
        """method_name [summary] make a string of method

        Args:
            method (str): [description] method name
            method_option (Dict[str, Any]): [description] option

        Returns:
            str: [description]  the string (all in one)
        """
        name = method
        option_str = ''
        if method_option:
            for key, value in method_option.items():
                if value is None:
                    pass
                elif isinstance(value, str):
                    if '/' in value or ':' in value or '\\' in value:
                        pass
                    else:
                        pair_str = '-' + key + '+' + str(value)
                        option_str += pair_str
                else:
                    pair_str = '-' + key + '+' + str(value)
                    option_str += pair_str
        # end if
        return name + option_str

    @staticmethod
    def parse_project(project_name: str
                      ) -> Tuple[str, str, Dict[str, str]]:
        """parse_project [summary] parse the problem name,
        modelling name and modelling options

        Args:
            project_name (str): [description] the whole project name

        Returns:
            Tuple[str, str, Dict[str, str]]: [description]
            problem name, modelling name, modelling options
        """
        # split
        project = project_name.split('-')
        assert len(project) >= 2
        problem = project[0]
        modelling = project[1]
        # prepare parse option
        option: Dict[str, str] = {}
        for pair in project[2:]:
            pair_list = pair.split('+')
            assert len(pair_list) == 2
            option[pair_list[0]] = pair_list[1]
        return problem, modelling, option

    @staticmethod
    def parse_method(method: str) -> Tuple[str, Dict[str, str]]:
        """parse_method [summary] parse the method name and options

        Args:
            method (str): [description] method string

        Returns:
            Tuple[str, Dict[str, str]]: [description]
            method name and options
        """
        # split
        method_list = method.split('-')
        assert len(method_list) >= 1
        method_name = method_list[0]
        # prepare parse option
        option: Dict[str, str] = {}
        for pair in method_list[1:]:
            pair_list = pair.split('+')
            assert len(pair_list) == 2
            option[pair_list[0]] = pair_list[1]
        return method_name, option

    @staticmethod
    def dump_dict(file_name: str, d: Dict[str, Any]) -> None:
        """dump_dict [summary] dump the dict into json file

        Args:
            file_name (str): [description] json file name
            d (Dict[str, Any]): [description] the dict
        """
        with open(file_name, 'w+') as file_out:
            json_object = json.dumps(d, indent=4)
            file_out.write(json_object)
            file_out.close()

    @staticmethod
    def dump_moip_solutions(file_name: str, parato_set: List[Any]) -> None:
        """dump_moip_solutions [summary] dump moip solutions

        Args:
            file_name (str): [description] file for dumpping
            parato_set (List[Any]): [description] the solutions
        """
        with open(file_name, 'w+') as file_out:
            for solution in parato_set:
                file_out.write(str(solution)+'\n')
            file_out.close()

    @staticmethod
    def dump_moip_variables(file_name: str, variables: List[Any]) -> None:
        """dump_moip_variables [summary] dump moip variables

        Args:
            file_name (str): [description] file for dumpping
            variables (List[Any]): [description] the variables
        """
        with open(file_name, 'w+') as file_out:
            for solution in variables:
                var_list = []
                for var in solution:
                    if var:
                        var_list.append(1)
                    else:
                        var_list.append(0)
                file_out.write(str(tuple(var_list))+'\n')
            file_out.close()

    @staticmethod
    def dump_debug(file, solutions):
        with open(file, 'w+') as fout:
            for solution in solutions:
                tmp_list = deepcopy(solution.objectives)
                tmp_list += solution.constraints
                if len(tmp_list) != 3:
                    continue
                fout.write(str(tuple(tmp_list)) + '\n')
            fout.close()

    @staticmethod
    def __prepare_task(task: Task) -> bool:
        # load config
        config = Config()
        # check task folder
        task_root = join(config.result_root_path, task.root_folder)
        if not isdir(task_root):
            makedirs(task_root, exist_ok=False)
        # check project folder
        project_name = Controller.project_name(task.problem, *task.modelling)
        project_folder = join(task_root, project_name)
        if not isdir(project_folder):
            makedirs(project_folder, exist_ok=False)
        # check method folder
        method_name = Controller.method_name(*task.method)
        method_folder = join(project_folder, method_name)
        if not isdir(method_folder):
            makedirs(method_folder, exist_ok=False)
        # check if need dump problem
        return task.method[0] in config.dump_method

    @staticmethod
    def run_moea_task(task: Task) -> None:
        # check dump folder
        config = Config()
        if not isdir(config.dump_path):
            makedirs(config.dump_path, exist_ok=False)
        # prepare folders
        project_name = Controller.project_name(task.problem, *task.modelling)
        method_name = Controller.method_name(*task.method)
        method_folder = join(config.result_root_path, task.root_folder,
                             project_name, method_name)
        # prepare problem
        nrp_problem = NextReleaseProblem(task.problem)
        nrp_problem.premodel(task.modelling[1])
        # dump problem
        problem_file = abspath(join(config.dump_path, project_name + '.json'))
        # xuan_binary dump for itself
        sub_option: Dict[str, Any] = {}
        if config.parse_dataset_keyword(task.problem) == 'xuan':
            # TODO: could be better
            NextReleaseProblem.dump_xuan(problem_file, task.problem,
                                         nrp_problem.nrp)
            if task.modelling[0] == 'bincst':
                sub_option['xuan'] = task.modelling[1]['bound']
            elif task.modelling[0] == 'binary':
                sub_option['xuan'] = -1.0
            elif task.modelling[0] == 'triurgency':
                sub_option['xuan'] = -10.0
        else:
            problem = nrp_problem.model(task.modelling[0], task.modelling[1])
            NextReleaseProblem.dump_nrp(problem_file, problem)
        option = task.method[1]
        if 'iteration' not in option:
            option['iteration'] = 1
        option['problem_name'] = project_name
        option['dump_path'] = abspath(config.dump_path)
        option['result_path'] = abspath(method_folder)
        option.update(sub_option)
        # employ a solver
        solver = Solver(task.method[0], option, problem_file)
        solver.prepare()
        solver.execute()

    @staticmethod
    def run_moip_task(task: Task) -> None:
        # prepare folders
        config = Config()
        project_name = Controller.project_name(task.problem, *task.modelling)
        method_name = Controller.method_name(*task.method)
        method_folder = join(config.result_root_path, task.root_folder,
                             project_name, method_name)
        # prepare problem
        nrp_problem = NextReleaseProblem(task.problem)
        nrp_problem.premodel(task.modelling[1])
        nrp = nrp_problem.model(*task.modelling)
        # get iteration num
        if 'iteration' in task.method[1]:
            iteration = task.method[1]['iteration']
        else:
            iteration = 1
        # run iteration_num times
        for itr in range(iteration):
            # employ a solver
            solver = Solver(*task.method, nrp)
            # solve
            start_time = clock()
            solver.prepare()
            solver.execute()
            elapsed_time = clock() - start_time
            solutions = solver.solutions()
            # dump solutions
            solutions_file = join(method_folder, 's_' + str(itr) + '.txt')
            Controller.dump_moip_solutions(solutions_file, solutions)
            # dump variables
            variables = solver.variables()
            variables_file = join(method_folder, 'v_' + str(itr) + '.txt')
            Controller.dump_moip_variables(variables_file, variables)
            # dump other info
            info_file = join(method_folder, 'i_' + str(itr) + '.json')
            info: Dict[str, Any] = {}
            info['elapsed time'] = round(elapsed_time, 2)
            info['solutions found'] = len(solutions)
            Controller.dump_dict(info_file, info)
        # end for

    @staticmethod
    def run_task(task: Task) -> None:
        # prepare result folders, get if need dump
        need_dump = Controller.__prepare_task(task)
        # run moip task
        if need_dump:
            Controller.run_moea_task(task)
        # run moea task
        else:
            Controller.run_moip_task(task)

    @staticmethod
    def run(task_file: str) -> None:
        """run [summary] run for a task file

        Args:
            task_file (str): [description] task file
        """
        # load config
        config = Config()
        file_name = join(config.task_path, task_file)
        task_list = Controller.parse_tasks(Controller.load_json(file_name))
        for task in task_list:
            gc.collect()
            print(task)
            Controller.run_task(task)
        # end for
