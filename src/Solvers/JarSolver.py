#
# DONG Shi, dongshi@mail.ustc.edu.cn
# JarSolver.py, created: 2020.11.05
# last modified: 2020.11.07
#

from typing import Dict, Any
import json
from os.path import join, abspath
import subprocess
from src.Config import Config


class JarSolver:
    def __init__(self, method: str,
                 method_option: Dict[str, Any]) -> None:
        """__init__ [summary] JarSolver is an interface for
        running *.jar algorithms

        Args:
            method (str): [description] solver name
            method_option (Dict[str, Any]): [description] option
        """
        # store members
        self.method = method
        self.option = method_option
        # command line order
        self.cmd = '{} -jar {} {}'

    def prepare(self):
        """prepare [summary] prepare for running
        """
        # find the problem path in problem
        dump_path = self.option['dump_path']
        problem_name = self.option['problem_name']
        config_file = join(dump_path, 'config-' + problem_name + '.json')
        # dump the option
        with open(config_file, 'w+') as file_out:
            json_object = json.dumps(self.option, indent=4)
            file_out.write(json_object)
            file_out.close()
        # prepare command
        jar_file = join('src/Solvers/', '{}Solver.jar'.format(self.method))
        config = Config()
        self.cmd = self.cmd.format(config.java_exe,
                                   abspath(jar_file),
                                   abspath(config_file))

    def execute(self):
        """execute [summary] run the jar algorithm
        """
        # call the algorithm
        print('exec> ' + self.cmd)
        subprocess.run(self.cmd)
