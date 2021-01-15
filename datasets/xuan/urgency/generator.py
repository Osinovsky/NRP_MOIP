from random import randint
from json import dump

requirement_num = {
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

for project, req_num in requirement_num.items():
    if project.startswith('realistic'):
        urgency = [randint(1, 9) for _ in range(req_num)]
        with open(project + '.json', 'w') as fout:
            dump(urgency, fout)
            fout.close()
