#
# DONG Shi, dongshi@mail.ustc.edu.cn
# JarSolver.py, created: 2020.11.05
# last modified: 2020.11.05
#

from typing import Dict, Any
import json
from os.path import join
# import subprocess


class JarSolver:
    def __init__(self, method: str,
                 method_option: Dict[str, Any],
                 problem: str) -> None:
        """__init__ [summary] JarSolver is an interface for
        running *.jar algorithms

        Args:
            method (str): [description] solver name
            method_option (Dict[str, Any]): [description] option
            problem (str): [description] problem file name
        """
        # find the problem path in problem
        dump_path = method_option['dump_path']
        problem_name = method_option['problem_name']
        config_file = join(dump_path, 'config-' + problem_name + '.json')
        # dump the option
        with open(config_file, 'w+') as file_out:
            json_object = json.dumps(method_option, indent=4)
            file_out.write(json_object)
            file_out.close()
        # call the algorithm
        pass