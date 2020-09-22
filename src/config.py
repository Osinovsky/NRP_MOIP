# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.08.25     #
# Last Modified: 2020.09.20          #
# ################################## #

from os import path

# FILES PATH AND NAMES
# output path
RESULT_PATH = '../result/'

# input file pathes
# Xuan's Datasets
CLASSIC_NRP_PATH = '../datasets/xuan/classic-nrp/'
CLASSIC_NRPS = ['nrp1.txt', 'nrp2.txt', 'nrp3.txt', 'nrp4.txt', 'nrp5.txt']
REALISTIC_NRP_PATH = '../datasets/xuan/realistic-nrp/'
REALISTIC_NRPS = ['nrp-e1.txt', 'nrp-e2.txt', 'nrp-e3.txt', 'nrp-e4.txt', 'nrp-g1.txt', 'nrp-g2.txt', 'nrp-g3.txt', 'nrp-g4.txt', 'nrp-m1.txt', 'nrp-m2.txt', 'nrp-m3.txt', 'nrp-m4.txt']
# The Motorola Dateset
MOTOROLA_FILE_NAME = '../datasets/motorola/motorola.txt'
# RALIC Dataset(s), RateP
RALIC_PATH = '../datasets/RALIC/'
RALIC_COST_FILE = 'RALIC_requirements_and_cost.txt'
RALIC_PREFIX = ['Point', 'Rank', 'Rate']
RALIC_FILE = {'obj' : '{0}P-Obj.txt', 'req' : '{0}P-Req.txt', 'sreq' : '{0}P-SReq.txt'}
# Baan Dataset
BAAN_FILE_NAME = '../datasets/Baan/Baan.xls'
BAAN_SHEET_NAME = 'all requirements'
BAAN_BOUNDARY = {'left': 4, 'right': 22, 'up' : 1, 'down' : 101}

# make the file path more friendly, code them into a big dict
ALL_FILES_DICT = { \
    'classic_1' : path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[0]), \
    'classic_2' : path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[1]), \
    'classic_3' : path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[2]), \
    'classic_4' : path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[3]), \
    'classic_5' : path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[4]), \
    'realistic_e1' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[0]), \
    'realistic_e2' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[1]), \
    'realistic_e3' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[2]), \
    'realistic_e4' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[3]), \
    'realistic_g1' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[4]), \
    'realistic_g2' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[5]), \
    'realistic_g3' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[6]), \
    'realistic_g4' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[7]), \
    'realistic_m1' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[8]), \
    'realistic_m2' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[9]), \
    'realistic_m3' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[10]), \
    'realistic_m4' : path.join(REALISTIC_NRP_PATH , REALISTIC_NRPS[11]), \
    'Motorola' : MOTOROLA_FILE_NAME, \
    'RALIC_Point' : {'obj' : path.join(RALIC_PATH, RALIC_FILE['obj'].format('Point')), \
                     'req' : path.join(RALIC_PATH, RALIC_FILE['req'].format('Point')), \
                     'sreq' : path.join(RALIC_PATH, RALIC_FILE['sreq'].format('Point')), \
                     'cost' : path.join(RALIC_PATH, RALIC_COST_FILE)}, \
    'RALIC_Rank' : {'obj' : path.join(RALIC_PATH, RALIC_FILE['obj'].format('Rank')), \
                    'req' : path.join(RALIC_PATH, RALIC_FILE['req'].format('Rank')), \
                    'sreq' : path.join(RALIC_PATH, RALIC_FILE['sreq'].format('Rank')), \
                    'cost' : path.join(RALIC_PATH, RALIC_COST_FILE)}, \
    'RALIC_Rate' : {'obj' : path.join(RALIC_PATH, RALIC_FILE['obj'].format('Rate')), \
                    'req' : path.join(RALIC_PATH, RALIC_FILE['req'].format('Rate')), \
                    'sreq' : path.join(RALIC_PATH, RALIC_FILE['sreq'].format('Rate')), \
                    'cost' : path.join(RALIC_PATH, RALIC_COST_FILE)}, \
    'Baan' : BAAN_FILE_NAME, \
}

# NRP MODELLING FROMS
NRP_FORMS = ['single', 'binary']

# SOLVERS
SOLVING_METHOD = ['single', 'epsilon', 'CWMOIP', 'ncgol']