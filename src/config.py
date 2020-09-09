# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.08.25     #
# Last Modified: 2020.09.08          #
# ################################## #

from os import path

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
RATEP_OBJ_FILE = 'RateP-Obj.txt'
RATEP_REQ_FILE = 'RateP-Req.txt'
RATEP_SREQ_FILE = 'RateP-SReq.txt'

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
}
