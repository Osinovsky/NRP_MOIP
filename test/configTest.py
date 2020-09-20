# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.09.18     #
# Last Modified: 2020.09.18          #
# ################################## #

import unittest
import os
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from config import *

# test config.py
class configTest(unittest.TestCase):
    # files exist check
    def test_file_exist(self):
        for file_name in ALL_FILES_DICT.values():
            if isinstance(file_name, str):
                # other files
                assert os.path.exists(file_name)
            else:
                # RALIC files
                assert isinstance(file_name, dict)
                assert len(file_name) == 4
                # files inside the dict
                assert 'obj' in file_name
                assert os.path.exists(file_name['obj'])
                assert 'req' in file_name
                assert os.path.exists(file_name['req'])
                assert 'sreq' in file_name
                assert os.path.exists(file_name['sreq'])
                assert 'cost' in file_name
                assert os.path.exists(file_name['cost'])

# run the test
if __name__ == '__main__':
    unittest.main()