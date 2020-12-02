# HERE IS ON HOW TO GENERATE TASKS AUTOMATICLY

import json

file_name = 'bincst_test.json'

object = {
    "name": "xuan_bincst_test",
    "dataset": "classic",
    "modelling": [],
    "method": [
        {
            "name": "epsilon"
        },
        {
            "name": "cwmoip"
        }
    ]
}


def write_tasks(file_name, template, name, vals):
    with open(file_name, 'w+') as file:
        for value in vals:
            tmp_dict = {"name": "bincst"}
            tmp_dict[name] = value
            template['modelling'].append(tmp_dict)
        json.dump(template, file, indent=4)
        template['modelling'] = []
        file.close()


write_tasks('bincst_min_profit.json', object, 'min_profit', [0.3, 0.5, 0.7])
write_tasks('bincst_max_cost.json', object, 'max_cost', [0.3, 0.5, 0.7])
write_tasks('bincst_min_requirements.json', object,
            'min_requirements', [0.3, 0.5, 0.7])
write_tasks('bincst_min_customers.json', object,
            'min_customers', [0.3, 0.5, 0.7])
