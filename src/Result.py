#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Result.py, created: 2020.11.10
# last modified: 2020.11.12
#

from typing import Dict, Any, List, Tuple
import json
from os.path import join, isfile
from os import listdir
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from src.Config import Config


class ResultEntry:
    def __init__(self) -> None:
        """__init__ [summary] record one pareto's all results
        """
        # elapsed time
        self.time: float = 0.0
        # solutions found
        self.found: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive()
        # solutions on pareto front
        self.front: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive()
        # indicator scores
        self.score: Dict[str, float] = {}


class Result:
    def __init__(self, result_folder: str) -> None:
        """__init__ [summary] handle the result folders and files

        Args:
            result_folder (str): [description] result root folder
        """
        # result root
        config = Config()
        self.root = join(config.result_root_path, result_folder)

        # result template string
        self.info_template = join(self.root, '{}/{}/i_{}.json')
        self.vari_template = join(self.root, '{}/{}/v_{}.txt')
        self.sltn_template = join(self.root, '{}/{}/s_{}.txt')

        # load task file
        self.task = Result.load_json(join(self.root, 'task.json'))

        # project names
        self.projects: List[str] = \
            list(filter(lambda x: '.' not in x and x != 'comparison',
                        listdir(self.root)))
        assert len(self.projects) >= 1
        # method names
        first_project = join(self.root, self.projects[0])
        self.methods: List[str] = listdir(first_project)
        # iteration num
        first_method = join(first_project, self.methods[0])
        first_iterations = len(listdir(first_method))
        assert first_iterations % 3 == 0
        self.iterations: int = int(first_iterations / 3)

        # check for all files exist
        for p in self.projects:
            for m in self.methods:
                for i in range(self.iterations):
                    assert isfile(self.info_template.format(p, m, i))
                    assert isfile(self.vari_template.format(p, m, i))
                    assert isfile(self.sltn_template.format(p, m, i))
        # end nested for

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

    def method_name(self, method: str) -> str:
        """method_name [summary] find real method name

        Args:
            method (str): [description]

        Returns:
            str: [description] real name
        """
        flag = False
        real_name = ''
        for method_name in self.methods:
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
        method = self.method_name(method)
        assert iteration >= 0 and iteration < self.iterations
        return project, method, iteration

    def s(self, project: str, method: str, iteration: int) -> str:
        """s [summary] soltution file name

        Args:
            project (str): [description]
            method (str): [description]
            iteration (int): [description]

        Returns:
            str: [description] soltution file name
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.sltn_template.format(project, method, iteration)

    def v(self, project: str, method: str, iteration: int) -> str:
        """v [summary] variables file name

        Args:
            project (str): [description]
            method (str): [description]
            iteration (int): [description]

        Returns:
            str: [description] variables file name
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.vari_template.format(project, method, iteration)

    def i(self, project: str, method: str, iteration: int) -> str:
        """i [summary] infomation file name

        Args:
            project (str): [description]
            method (str): [description]
            iteration (int): [description]

        Returns:
            str: [description] infomation file name
        """
        # check arguments
        project, method, iteration = \
            self.check_arguments(project, method, iteration)
        return self.info_template.format(project, method, iteration)

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

    @staticmethod
    def dump_result_entry(folder: str, index: int, entry: ResultEntry) -> None:
        """dump_result_entry [summary] dump a result entry into
        three files: entry_{index}.json, front_{index}.archive,
        found_{index}.archive

        Args:
            folder (str): [description] folder name
            index (int): [description] index of entry in the list
            entry (ResultEntry): [description]
        """
        # dump entry
        entry_dict: Dict[str, Any] = {}
        entry_dict['time'] = entry.time
        entry_dict['score'] = entry.score
        entry_name = join(folder, 'entry_{}.json'.format(index))
        with open(entry_name, 'w+') as entry_file:
            json.dump(entry_dict, entry_file, indent=4)
            entry_file.close()
        # dump found
        Result.dump_archive(
            join(folder, 'found_{}.archive'.format(index)),
            entry.found
        )
        # dump front
        Result.dump_archive(
            join(folder, 'front_{}.archive'.format(index)),
            entry.front
        )

    @staticmethod
    def load_result_entry(folder: str, index: int) -> ResultEntry:
        """load_result_entry [summary] load result entry
        from three files: entry_{index}.json, front_{index}.archive,
        found_{index}.archive

        Args:
            folder (str): [description]
            index (int): [description]

        Returns:
            ResultEntry: [description]
        """
        entry = ResultEntry()
        entry_name = join(folder, 'entry_{}.json'.format(index))
        with open(entry_name, 'r') as entry_file:
            entry_dict = json.load(entry_file)
            entry_file.close()
        entry.time = entry_dict['time']
        entry.score = entry_dict['score']
        entry.found = Result.load_archive(
            join(folder, 'found_{}.archive'.format(index))
        )
        entry.front = Result.load_archive(
            join(folder, 'front_{}.archive'.format(index))
        )
        return entry
