#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Config.py, created: 2020.10.31
# last modified: 2020.11.02
#

from typing import Dict, List
from os import path


class Config:
    """ [summary] Config class is used to store global configs

    Please update Config if you:
        update datasets
        update Loader
    """

    def __init__(self) -> None:
        # datasets
        self.dataset: Dict[str, str] = {}
        # datasets path
        self.dataset_path = './datasets/'
        # keywords, sub-dataset name: dataset name
        self.keywords = {
            'classic': 'xuan',
            'realistic': 'xuan'
        }

        # prepare datasets
        make_index_string = 'make_{}_index'
        for name in self.keywords:
            make_index = getattr(self, make_index_string.format(name))
            make_index()

        # model form
        self.modelling = \
            ['single', 'sincus', 'binary', 'bincst', 'trireq', 'tricus']
        # solvers
        self.solvers = ['single', 'epsilon', 'cwmoip', 'ncgop', 'NSGAII']

        # dump path
        self.dump_path = './dump/'

    def make_classic_index(self) -> None:
        """make_classic_index [summary] make classic datasets
        index in self.dataset
        """
        # classic nrp index
        classic_name = 'classic_{}'
        classic_format = 'xuan/classic-nrp/nrp{}.txt'
        for name in ['1', '2', '3', '4', '5']:
            self.dataset[classic_name.format(name)] = \
                path.join(self.dataset_path, classic_format.format(name))

    def make_realistic_index(self) -> None:
        """make_realistic_index [summary] make realistic datasets
        index in self.dataset
        """
        # realistic nrp index
        realistic_name = 'classic_{}'
        realistic_format = 'xuan/realistic-nrp/nrp-{}.txt'
        for name_left in ['e', 'm', 'g']:
            for name_right in ['1', '2', '3', '4']:
                name = name_left + name_right
                self.dataset[realistic_name.format(name)] = \
                    path.join(self.dataset_path, realistic_format.format(name))

    def get_index_dict(self, keywords: List[str]) -> Dict[str, str]:
        """get_index_dict [summary] get given keywords dataset subset

        Args:
            keywords (List[str]):
            [description] project name startswith keywords

        Returns:
            Dict[str, str]: [description] a map from name to file path
        """
        # check if keyword in keywords
        for keyword in keywords:
            assert keyword in self.keywords
        # prepare a tmp dict
        dataset_subset: Dict[str, str] = {}
        # traverse all entry in dataset
        for key in self.dataset:
            # try each keywords
            for keyword in keywords:
                if key.startswith(keyword):
                    dataset_subset[key] = self.dataset[key]
        # return
        return dataset_subset

    def parse_keyword(self, name: str) -> str:
        """parse_keyword [summary] parse the keyword in project name

        Args:
            name (str): [description] project name

        Returns:
            str: [description] the keyword
        """
        # should be in dataset
        assert name in self.dataset
        # find keyword by check startswith
        for keyword in self.keywords:
            if name.startswith(keyword):
                return keyword
        # if not found
        print('keyword lost as project: ', name)
        return ''

    def parse_dataset_keyword(self, name: str) -> str:
        """parse_dataset_keyword [summary] parse the keyword in project name
        but return the dataset name

        Args:
            name (str): [description] project name

        Returns:
            str: [description] dataset keyword
        """
        # should be in dataset
        assert name in self.dataset
        # find keyword by check startswith
        for keyword in self.keywords:
            if name.startswith(keyword):
                return self.keywords[keyword]
        # if not found
        print('keyword lost as project: ', name)
        return ''

    def dataset_names(self) -> List[str]:
        """dataset_names [summary] get all names of datasets

        Returns:
            List[str]: [description] datasets names
        """
        name_set = set()
        for keyword in self.keywords:
            name_set.add(self.keywords[keyword])
        return list(name_set)
