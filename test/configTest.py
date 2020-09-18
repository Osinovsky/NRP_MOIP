# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.09.18     #
# Last Modified: 2020.09.18          #
# ################################## #

import unittest
import os
import sys
sys.path.append("..")
from src.config import *

# test config.py
class configTest(unittest.TestCase):
    # files exist check
    def test_file_exist(self):
        for file_name in ALL_FILES_DICT.values():
            assert os.path.exists(file_name)

# run the test
if __name__ == '__main__':
    unittest.main()