# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# runnerTest.py, created: 2020.09.26 #
# Last Modified: 2020.09.26          #
# ################################## #

import unittest
import random
import os
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from config import *
from runner import Runner

class runnerTest(unittest.TestCase):
    # generate a random string
    def random_string(self):
        dictionary = 'abcdefzhijklmnopqrstuvwxyz'
        length = random.randint(3, 25)
        word = ''
        for _ in range(length):
            word += dictionary[random.randint(0, len(dictionary)-1)]
        return word

    # test for naming and denaming
    def test_name(self):
        for _ in range(1000): # loop for 1000 times
            project_name = list(ALL_FILES_DICT.keys())[random.randint(0, len(ALL_FILES_DICT)-1)]
            form = self.random_string()
            method = self.random_string()
            # prepare a dummy option
            option = dict()
            size = random.randint(0, 3)
            for _ in range(size):
                option[self.random_string()] = self.random_string()
            # name encode
            name = Runner.name(project_name, form, method, option)
            # decode name
            config = Runner.dename(name)
            # check 
            assert project_name == config['project']
            assert form == config['form']
            assert method == config['method']
            # ignore option

if __name__ == '__main__':
    unittest.main()