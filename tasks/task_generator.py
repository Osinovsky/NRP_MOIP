# HERE IS ON HOW TO GENERATE TASKS AUTOMATICLY

import json
from copy import deepcopy

file_name = 'bincst_test.json'

object = {
    "name": "xuan_bincst_test",
    "dataset": "classic_1",
    "modelling": [
        {
            "name": "bincst",
            "max_cost": 0.5,
            "min_profit": 0.5
        }
    ],
    "iteration": 1,
    "method": [
        {
            "name": "epsilon"
        },
        {
            "name": "cwmoip"
        }
    ]
}

with open(file_name, 'w+') as file:
    object_list = []
    for min_profit in [0.3, 0.5, 0.7]:
        object['modelling'][0]['min_profit'] = min_profit
        object_list.append(
            deepcopy(object)
        )
    json.dump(object_list, file, indent=4)
    file.close()
