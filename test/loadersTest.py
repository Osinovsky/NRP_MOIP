# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.09.18     #
# Last Modified: 2020.09.18          #
# ################################## #

import unittest
import os
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from loaders import Loader
from config import *

class loadersTest(unittest.TestCase):
    # test if all files are correct
    def test_load(self):
        for project_name in ALL_FILES_DICT.keys():
            loader = Loader(project_name)
            content = loader.load()
            if project_name.startswith('classic') or project_name.startswith('realistic'):
                # content should be (cost, dependencies, customers)
                assert len(content) == 3
                # should not empty, excluding dependencies
                assert content[0] and content[2]
            elif project_name.startswith('Motorola'):
                # content should be cost&revenue
                assert isinstance(content, list)
                # should not empty
                assert content
            elif project_name.startswith('RALIC'):
                # content should be levels
                assert content
            elif project_name.startswith('Baan'):
                # content should be (cost, profit)
                assert len(content) == 2
                # shoule not be empty
                assert content[0] and content[1]
            else:
                # shoule not be here
                assert False

if __name__ == '__main__':
    unittest.main()