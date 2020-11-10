#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Controller.py, created: 2020.11.02
# last modified: 2020.11.10
#

import json
from time import clock
from typing import Dict, Any, List, Union, Tuple, Set
from os import makedirs
from os.path import join, abspath
from src.Config import Config
from src.NRP import NextReleaseProblem
from src.Solver import Solver

# type
Entry = Tuple[str, Dict[str, Any]]


class Task:
    def __init__(self,
                 root_folder: str,
                 iteration_num: int,
                 problems: List[str],
                 modelling: Entry,
                 methods: List[Entry]
                 ) -> None:
        """__init__ [summary] define members
        """
        self.root_folder: str = root_folder
        self.iteration_num: int = iteration_num
        self.problems: List[str] = problems
        self.modelling: Entry = modelling
        self.methods: List[Entry] = methods

    def __str__(self) -> str:
        dict_object: Dict[str, Any] = {}
        dict_object['root_folder'] = self.root_folder
        dict_object['iteration_num'] = str(self.iteration_num)
        dict_object['problem'] = self.problems
        dict_object['modelling'] = self.modelling
        method_dict: Dict[str, Any] = {}
        for entry in self.methods:
            method_dict[entry[0]] = entry[1]
        dict_object['methods'] = method_dict
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
        # prepare task list
        task_list: List[Task] = []

        # find the task name
        assert 'name' in task
        task_name: str = task['name']
        # find the iteration num
        assert 'iteration' in task
        iteration_num: int = task['iteration']

        # parse the datasets
        assert 'dataset' in task
        dataset = task['dataset']
        # gather all problems it needs
        problems: Set[str] = set()
        if isinstance(dataset, str):
            dataset = [dataset]
        for name in dataset:
            type = config.name_type(name)
            if type == 'problem':
                problems.add(name)
            elif type == 'keyword':
                problems.update(set(config.keyword_cluster(name)))
            elif type == 'dataset':
                problems.update(set(config.dataset_cluster(name)))
            else:
                print(name, ' not exists')
        # end for
        problems_list: List[str] = list(problems)

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

        # parse the modelling
        assert 'modelling' in task
        formatting = task['modelling']
        if isinstance(formatting, dict):
            formatting = [formatting]
        for modelling in formatting:
            assert 'name' in modelling
            modelling_name = modelling['name']
            assert modelling_name in config.modelling
            del modelling['name']
            # create a task
            one_task = Task(
                task_name,
                iteration_num,
                problems_list,
                (modelling_name, modelling),
                methods
            )
            task_list.append(one_task)
        # end for
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
                if value is not None:
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
                if value:
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
    def dump_moip_solutions(file_name: str, parato_set: Set[Any]) -> None:
        """dump_moip_solutions [summary] dump moip solutions

        Args:
            file_name (str): [description] file for dumpping
            parato_set (Set[Any]): [description] the solutions
        """
        with open(file_name, 'w+') as file_out:
            for solution in parato_set:
                file_out.write(str(solution)+'\n')
            file_out.close()

    @staticmethod
    def dump_moip_variables(file_name: str, variables: Set[Any]) -> None:
        """dump_moip_variables [summary] dump moip variables

        Args:
            file_name (str): [description] file for dumpping
            variables (Set[Any]): [description] the variables
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
    def run_task(task: Task):
        # load config
        config = Config()
        # result folder
        task_root = join(config.result_root_path, task.root_folder)
        makedirs(task_root, exist_ok=True)
        # dump task dict in this folder
        with open(join(task_root, 'task.json'), 'w+') as task_file:
            task_file.write(str(task))
            task_file.close()
        # end for
        # load problems
        for problem_name in task.problems:
            nrp_problem = NextReleaseProblem(problem_name)
            nrp_problem.premodel(task.modelling[1])
            nrp = nrp_problem.model(*task.modelling)
            # make problem folder name
            project_name = \
                Controller.project_name(problem_name, *task.modelling)
            problem_folder = join(task_root, project_name)
            makedirs(problem_folder, exist_ok=True)
            # prepare dump path
            dump_path = join(config.dump_path, task.root_folder)

            # for each method, run on the problem
            for method, option in task.methods:
                # prepare method folder
                method_folder = join(problem_folder,
                                     Controller.method_name(method, option))
                makedirs(method_folder, exist_ok=True)
                # dump solvers
                if config.if_dump(method):
                    makedirs(dump_path, exist_ok=True)
                    # prepare dump file name
                    problem = abspath(join(dump_path, project_name + '.json'))
                    NextReleaseProblem.dump(problem,
                                            nrp.variables,
                                            nrp.objectives,
                                            nrp.inequations)
                    # prepare some running option for dump solver
                    option['problem_name'] = project_name
                    option['dump_path'] = abspath(dump_path)
                    option['result_path'] = abspath(method_folder)
                    option['iteration'] = task.iteration_num
                    # employ a solver
                    solver = Solver(method, option, problem)
                    solver.prepare()
                    solver.execute()
                else:
                    # run iteration_num times
                    for itr in range(task.iteration_num):
                        # employ a solver
                        solver = Solver(method, option, nrp)
                        # solve
                        start_time = clock()
                        solver.prepare()
                        solver.execute()
                        elapsed_time = clock() - start_time
                        # moip need dump solutions and runtime manually
                        if method in config.moip_method:
                            solutions = solver.solutions()
                            # dump solutions
                            solutions_file = join(method_folder,
                                                  's_' + str(itr) + '.txt')
                            Controller.dump_moip_solutions(solutions_file,
                                                           solutions)
                            # dump variables
                            variables = solver.variables()
                            variables_file = join(method_folder,
                                                  'v_' + str(itr) + '.txt')
                            Controller.dump_moip_variables(variables_file,
                                                           variables)
                            # dump other info
                            info_file = join(method_folder,
                                             'i_' + str(itr) + '.json')
                            info: Dict[str, Any] = {}
                            info['elapsed time'] = round(elapsed_time, 2)
                            info['solutions found'] = len(solutions)
                            Controller.dump_dict(info_file, info)
                        # end if
                    # end for
                # end if
            # end for

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
            print(task)
            Controller.run_task(task)
        # end for
