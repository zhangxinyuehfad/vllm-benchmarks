import os
from pathlib import Path
from typing import Union
from handler import DataHandler


def read_from_file(file_path: Union[str, Path]):
    res = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts  = line.split(' ', 1)
            commit_id, commit_title = parts[0], parts[1]
            res[commit_id] = commit_title
    return res

data_handler = DataHandler()
data_handler.index_name = 'vllm_benchmark_throuthput'
