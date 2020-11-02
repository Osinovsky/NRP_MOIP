#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Controller.py, created: 2020.11.02
# last modified: 2020.11.02
#

import json
from typing import Dict, Any, List
from Config import Config


class Controller:
    def __init__(self) -> None:
        """__init__ [summary] define members
        """
        pass

    @staticmethod
    def load_json(json_file: str) -> Dict[str, Any]:
        """load_json [summary] load json file

        Args:
            json_file (str): [description] *.json file name

        Returns:
            Dict[str, Any]: [description] return the dict content in that file
        """
        data = None
        with open(json_file, 'r') as fin:
            data = json.load(fin)
            fin.close()
        return data

    def parse_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        # load config
        config = Config()
        # find the task name
        assert 'name' in task
        task_name = task['name']
        # parse the datasets
        assert 'dataset' in task
        dataset = task['dataset']
        # gather all problems it needs
        problems = set()
        if isinstance(dataset, str):
            dataset = [dataset]
        for name in dataset:
            type = config.name_type(name)
            if type == 'name':
                problems.add(name)
            elif type == 'keyword':
                problems.union(set(config.keyword_cluster(name)))
            elif type == 'dataset':
                problems.union(set(config.dataset_cluster(name)))
            else:
                print(name, ' not exists')
        # parse the modelling
        assert 'modelling' in task
        formatting = task['modelling']
        modelling = dict()
        if isinstance(formatting, dict):
            formatting = [formatting]
        for mdl in formatting:
            assert 'name' in mdl
            modelling_name = mdl['name']
            assert modelling_name in config.modelling
            del mdl['name']
            modelling[modelling_name] = mdl
        # parse the methods
        assert 'method' in task
        algorithms = task['method']
        method = dict()
        if isinstance(algorithms, dict):
            algorithms = [algorithms]
        for algorithm in algorithms:
            assert 'name' in algorithm
            method_name = algorithm['name']
            assert method_name in config.method
            del algorithm['name']
            method[method_name] = algorithm
        # TODO: turn task into sub-task set and return
        task_list: List[Dict[str, Any]] = []
        
        return task_list
