import os
from pathlib import Path
from typing import Union


def read_from_file(file_path: Union[str, Path]):
    with open(file_path, 'r') as f:
        data  = str.split(' ', 1)
        commit_id, commit_title 