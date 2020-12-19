from ast import literal_eval as make_tuple
from os.path import join


def cut_head(name, start):
    seeds = []
    with open(name, 'r') as fin:
        for line in fin.readlines():
            if not line:
                continue
            seed = make_tuple(line)[start:]
            seeds.append(seed)
        fin.close()

    with open(name, 'w') as fout:
        for seed in seeds:
            fout.write(str(seed) + '\n')
        fout.close()


def check_seed(name, length):
    with open(name, 'r') as fin:
        for line in fin.readlines():
            if not line:
                continue
            assert length == len(make_tuple(line))
        fin.close()


root = './binary/'
cut_dict = {
    'classic_1': 100,
    'classic_2': 500,
    'classic_3': 500,
    'classic_4': 750,
    'classic_5': 1000,
    'realistic_e1': 536,
    'realistic_e2': 491,
    'realistic_e3': 456,
    'realistic_e4': 399,
    'realistic_g1': 445,
    'realistic_g2': 315,
    'realistic_g3': 423,
    'realistic_g4': 294,
    'realistic_m1': 768,
    'realistic_m2': 617,
    'realistic_m3': 765,
    'realistic_m4': 568
}
req_dict = {
    'classic_1': 140,
    'classic_2': 620,
    'classic_3': 1500,
    'classic_4': 3250,
    'classic_5': 1500,
    'realistic_e1': 3502,
    'realistic_e2': 4254,
    'realistic_e3': 2844,
    'realistic_e4': 3186,
    'realistic_g1': 2690,
    'realistic_g2': 2650,
    'realistic_g3': 2512,
    'realistic_g4': 2246,
    'realistic_m1': 4060,
    'realistic_m2': 4368,
    'realistic_m3': 3566,
    'realistic_m4': 3643
}

# name = 'classic_5'

tasks = ['realistic_e2', 'realistic_e3', 'realistic_e4',
         'realistic_g1', 'realistic_g2', 'realistic_g3', 'realistic_g4',
         'realistic_m1', 'realistic_m2', 'realistic_m3', 'realistic_m4']
for name in tasks:
    cut_head(join(root, name + '.txt'), cut_dict[name])
    check_seed(join(root, name + '.txt'), req_dict[name])
