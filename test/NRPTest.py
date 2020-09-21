# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# NRPTest.py, created: 2020.09.21    #
# Last Modified: 2020.09.21          #
# ################################## #

import unittest
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from NRP import NextReleaseProblem
from config import *

class NRPTest(unittest.TestCase):
    # test inventory
    def test_inventory(self):
        for project_name in ALL_FILES_DICT.keys():
            # assert is in NRP initialization
            nrp = NextReleaseProblem(project_name)

if __name__ == '__main__':
    unittest.main()