#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Result.py, created: 2020.11.10
# last modified: 2021.01.19
#

from typing import Dict, Any, List, Tuple
import json
from os.path import join, isfile
from os import listdir
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from src.Config import Config


class Result:
    def __init__(self, result_folder: str,
                 use_cached_front: bool = True) -> None:
        """__init__ [summary] handle the result folders and files

        Args:
            result_folder (str): [description] result root folder
            use_cached_front (bool): [description] if use .front files
            if available
        """
        # result root
        config = Config()
        self.root = join(config.result_root_path, result_folder)
        self.use_cached_front = use_cached_front

        # result template string
        self.info_template = join(self.root, '{}/{}/i_{}.json')
        self.vari_template = join(self.root, '{}/{}/v_{}.txt')
        self.sltn_template = join(self.root, '{}/{}/s_{}.txt')

        # method pareto front template
        self.method_front_template = join(self.root, '{}/{}/.front')
        # project pareto front template
        self.project_front_template = join(self.root, '{}/.front')

        # project names
        self.projects: List[str] = \
            list(filter(lambda x: not x.startswith('.'), listdir(self.root)))
        assert len(self.projects) >= 1
        # method names and iteration num
        self.methods: Dict[str, List[str]] = {}
        self.iterations: Dict[Tuple[str, str], int] = {}

        # check for all files exist
        for p in self.projects:
            self.methods[p] = \
                list(filter(lambda x: not x.startswith('.'),
                            listdir(join(self.root, p))))
            for m in self.methods[p]:
                files = listdir(join(self.root, p, m))
                iteration = len([f for f in files if f.startswith('i_')])
                self.iterations[(p, m)] = iteration
                for i in range(iteration):
                    assert isfile(self.info_template.format(p, m, i))
                    assert isfile(self.vari_template.format(p, m, i))
                    assert isfile(self.sltn_template.format(p, m, i))
        # end nested for

        # infomation
        self.info: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.load_info()

        # prepare non-dominated solutions count
        self.non_dominated_count: Dict[Tuple[str, str], int] = {}

        # prepare pareto fronts
        self.project_fronts: Dict[str, NonDominatedSolutionsArchive] = {}
        self.method_fronts: Dict[Tuple[str, str],
                                 NonDominatedSolutionsArchive] = {}
        for project in self.projects:
            for method in self.methods[project]:
                print(project, method)
                self.build_method_front(project, method)
            self.build_project_front(project)
        # end for

    def find_worst_point(self, project: str) -> List[Any]:
        """find_worst_point [summary] find a worst point
        construct from worst value in each dimension
        Args:
            project (str): [description]
        Returns:
            List[Any]: [description] reference point
        """
        point: List[Any] = []
        for method in self.methods[project]:
            key = (project, method)
            for solution in self.method_fronts[key].solution_list:
                if not point:
                    point = solution.objectives
                else:
                    for dim in range(len(point)):
                        obj = solution.objectives[dim]
                        if obj > point[dim]:
                            point[dim] = obj
        point = [x + 1.0 for x in point]
        # for method in self.methods[project]:
        #     key = (project, method)
        #     for solution in self.method_fronts[key].solution_list:
        #         for ind, obj in enumerate(solution.objectives):
        #             assert point[ind] > obj
        return point

    def build_method_front(self, project: str, method: str) -> None:
        """build_method_front [summary] build pareto front for
        a certain method on a certain project

        Args:
            project (str): [description]
            method (str): [description]
        """
        # use .front if possible
        if isfile(self.mf(project, method)) and self.use_cached_front:
            self.method_fronts[(project, method)] = \
                self.load_archive(self.mf(project, method))
            return
        # build pareto
        solution_files = []
        for i in range(self.iterations[(project, method)]):
            solution_files.append((
                self.s(project, method, i),
                self.v(project, method, i)
            ))
        self.method_fronts[(project, method)] = \
            self.build_pareto_front(solution_files)
        # write into .front file
        self.dump_archive(join(self.root, project, method, '.front'),
                          self.method_fronts[(project, method)])

    def build_project_front(self, project: str) -> None:
        """build_project_front [summary] build pareto front for
        a certain project, by every solutions found by each method

        Args:
            project (str): [description]
        """
        # use .front if possible
        if isfile(self.pf(project)) and self.use_cached_front:
            self.project_fronts[(project)] = \
                self.load_archive(self.pf(project))
            # load non dominated count
            tmp_dict = \
                self.load_json(self.pf(project) + '.count')
            for k, v in tmp_dict.items():
                key = (k.split('|')[0], k.split('|')[1])
                self.non_dominated_count[key] = int(v)
            return
        # use method fronts to build project front
        archive = NonDominatedSolutionsArchive()
        for method in self.methods[project]:
            key = (project, method)
            assert key in self.method_fronts
            for solution in self.method_fronts[key].solution_list:
                archive.add(solution)
        for method in self.methods[project]:
            key = (project, method)
            self.non_dominated_count[key] = 0
            for solution in self.method_fronts[key].solution_list:
                s_obj = solution.objectives
                for pareto_solution in archive.solution_list:
                    if s_obj == pareto_solution.objectives:
                        self.non_dominated_count[key] += 1
                        break
        self.project_fronts[project] = archive
        # write into .front and .front.count
        self.dump_archive(self.pf(project), archive)
        tmp_dict = {k[0] + '|' + k[1]: v for k, v
                    in self.non_dominated_count.items()}
        with open(self.pf(project) + '.count', 'w') as fout:
            json.dump(tmp_dict, fout)
            fout.close()

    @staticmethod
    def build_pareto_front(solution_files: List[Tuple[str, str]]
                           ) -> NonDominatedSolutionsArchive:
        """build_pareto_front [summary] build pareto front for
        give solution files.
        Note that, solution_files are [(s_file, v_file)]

        Args:
            solution_files (List[Tuple[str, str]]): [description]
            zip of solution files and variables files

        Returns:
            NonDominatedSolutionsArchive: [description]
        """
        archive = NonDominatedSolutionsArchive()
        for solution_file in solution_files:
            solutions = \
                Result.load_solutions(solution_file[0], solution_file[1])
            for solution in solutions:
                archive.add(solution)
        return archive

    @staticmethod
    def quick_prob(result_folder: str) -> None:
        config = Config()
        root = join(config.result_root_path, result_folder)
        projects = [x for x in listdir(root) if not isfile(x)]
        for project in projects:
            print(project + ':')
            methods = list(filter(lambda x: not x.startswith('.'),
                           listdir(join(root, project))))
            for method in methods:
                if len(method) > 10:
                    method_name = method[:8] + '..'
                else:
                    method_name = method
                print(method_name + '\t', end='')
                infos = list(filter(lambda x: x.startswith('i_'),
                             listdir(join(root, project, method))))
                for i_f in infos:
                    info = Result.load_json(join(root, project, method, i_f))
                    time = str(round(info['elapsed time'], 2))
                    found = str(info['solutions found'])
                    print(time + '\t' + found + '\t', end='')
                print()

    @staticmethod
    def load_json(file_name: str) -> Dict[str, Any]:
        """load_json [summary] load a json file into dict

        Args:
            file_name (str): [description] *.json file name

        Returns:
            Dict[str, Any]: [description] json dict
        """
        json_object: Dict[str, Any] = {}
        with open(file_name, 'r') as json_file:
            json_object = json.load(json_file)
            json_file.close()
        return json_object

    def load_info(self) -> None:
        for p in self.projects:
            for m in self.methods[p]:
                tmp_info: Dict[str, Any] = {}
                tmp_info['found'] = 0
                tmp_info['time'] = .0
                for i in range(self.iterations[(p, m)]):
                    info = Result.load_json(
                        self.i(p, m, i)
                    )
                    tmp_info['found'] += int(info['solutions found'])
                    tmp_info['time'] += float(info['elapsed time'])
                self.info[(p, m)] = tmp_info
        # end nest for

    def project_name(self, project: str) -> str:
        """project_name [summary] find real project name

        Args:
            project (str): [description]

        Returns:
            str: [description] real name
        """
        flag = False
        real_name = ''
        for project_name in self.projects:
            if project_name.startswith(project):
                real_name = project_name
                flag = True
        assert flag
        return real_name

    def method_name(self, project: str, method: str) -> str:
        """method_name [summary] find real method name

        Args:
            project (str): [description]
            method (str): [description]

        Returns:
            str: [description] real name
        """
        flag = False
        real_name = ''
        for method_name in self.methods[project]:
            if method_name.startswith(method):
                real_name = method_name
                flag = True
        assert flag
        return real_name

    def check_arguments(self, project: str,
                        method: str,
                        iteration: int
                        ) -> Tuple[str, str, int]:
        """check_arguments [summary] check three keys

        Args:
            project (str): [description]
            method (str): [description]
            iteration (int): [description]

        Returns:
            Tuple[str, str, int]: [description] three keys
        """
        project = self.project_name(project)
        assert method in self.methods[project]
        method = self.method_name(project, method)
        assert iteration >= 0 \
            and iteration < self.iterations[(project, method)]
        return project, method, iteration

    def s(self, project: str, method: str, iteration: int) -> str:
        """ solution file(objectives)
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.sltn_template.format(project, method, iteration)

    def v(self, project: str, method: str, iteration: int) -> str:
        """ variables file
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.vari_template.format(project, method, iteration)

    def i(self, project: str, method: str, iteration: int) -> str:
        """ infomation file
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.info_template.format(project, method, iteration)

    def mf(self, project: str, method: str) -> str:
        """ method front file
        """
        return self.method_front_template.format(project, method)

    def pf(self, project: str) -> str:
        """ project front file
        """
        return self.project_front_template.format(project)

    @staticmethod
    def tuple_parse(tuple_str: str, element_type: type) -> Tuple[Any, ...]:
        """tuple_parse [summary] parse tuple from string
        with a give element type

        Args:
            tuple_str (str): [description]
            element_type (type): [description]

        Returns:
            Tuple[Any, ...]: [description] tuple
        """
        # tuple list
        tuple_list: List[Any] = []
        # ignore characters
        ignore = ' \t\b\r\n('
        # terminate chracters
        terminate = '),'
        # recording string
        recording = ''
        for ch in tuple_str:
            if ch in ignore:
                pass
            elif ch in terminate:
                if element_type == bool:
                    if recording == '1':
                        tuple_list.append(True)
                    elif recording == '0':
                        tuple_list.append(False)
                    else:
                        assert False
                else:
                    tuple_list.append(element_type(recording))
                recording = ''
            else:
                recording += ch
        # return tuple
        return tuple(tuple_list)

    @staticmethod
    def load_tuples(file_name: str, element_type: type
                    ) -> List[Tuple[Any, ...]]:
        """load_tuples [summary] load tuples of int/float/bool from file

        Args:
            file_name (str): [description]
            element_type (type): [description]
        Returns:
            List[Tuple[Any, ...]]: [description] tuples
        """
        # read from files
        lines = None
        with open(file_name, 'r') as fin:
            # read lines
            lines = fin.readlines()
            fin.close()
        # parse each line into tuple
        tuples: List[Tuple[Any, ...]] = []
        for line in lines:
            if line.strip():
                tuples.append(Result.tuple_parse(line, element_type))
        # end for
        return tuples

    @staticmethod
    def load_solutions(objectives_file: str,
                       variables_file: str
                       ) -> List[BinarySolution]:
        # load objectives and variables
        objectives = Result.load_tuples(objectives_file, float)
        variables = Result.load_tuples(variables_file, bool)
        assert len(objectives) == len(variables)
        # prepare
        objectives_len = len(objectives[0])
        variables_len = len(variables[0])
        solutions_num = len(objectives)
        solutions: List[BinarySolution] = []
        # make BinarySolution s
        for i in range(solutions_num):
            solution = BinarySolution(
                variables_len,
                objectives_len)
            solution.variables = [list(variables[i])]
            solution.objectives = list(objectives[i])
            solutions.append(solution)
        # end for
        return solutions

    @staticmethod
    def dump_archive(file_name: str,
                     archive: NonDominatedSolutionsArchive) -> None:
        """dump_archive [summary] dump an archive

        Args:
            file_name (str): [description]
            archive (NonDominatedSolutionsArchive): [description]
        """
        with open(file_name, 'w+') as archive_file:
            for solution in archive.solution_list:
                solution_str = Result.solution_string(solution)
                archive_file.write(solution_str + '\n')
            archive_file.close()

    @staticmethod
    def load_archive(file_name: str) -> NonDominatedSolutionsArchive:
        """load_archive [summary] load an archive from file

        Args:
            file_name (str): [description]

        Returns:
            NonDominatedSolutionsArchive: [description]
        """
        archive = NonDominatedSolutionsArchive()
        with open(file_name, 'r') as archive_file:
            for solution_str in archive_file:
                solution = Result.parse_solution(solution_str)
                archive.add(solution)
            archive_file.close()
        return archive

    @staticmethod
    def solution_string(solution: BinarySolution) -> str:
        """solution_string [summary] convert solution into
        a json string

        Args:
            solution (BinarySolution): [description]

        Returns:
            str: [description] json string
        """
        solution_dict: Dict[str, Any] = {}
        solution_dict['variables'] = [int(x) for x in solution.variables[0]]
        solution_dict['objectives'] = solution.objectives
        solution_dict['constraints'] = solution.constraints
        return json.dumps(solution_dict)

    @staticmethod
    def parse_solution(solution_str: str) -> BinarySolution:
        """parse_solution [summary] parse json to solution

        Args:
            solution_str (str): [description]

        Returns:
            BinarySolution: [description]
        """
        solution_dict = json.loads(solution_str)
        variables = [[bool(x) for x in solution_dict['variables']]]
        objectives = solution_dict['objectives']
        constraints = solution_dict['constraints']
        solution = BinarySolution(
            len(variables), len(objectives), len(constraints)
        )
        solution.variables = variables
        solution.objectives = objectives
        solution.constraints = constraints
        return solution
