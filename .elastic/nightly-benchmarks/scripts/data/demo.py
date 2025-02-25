from operator import ge
from pathlib import Path
import turtle


def get_all_commit(file_path):
    res = {}
    with open(file_path, 'r') as f:
        for line in f:
            commit= line.strip().split(' ', 1)
            commit_id, commit_title = commit[0], commit[1]
            res[commit_id] = commit_title
    return res

if __name__ == '__main__':
    print(get_all_commit('/Users/wangli/vllm-ascend/commit_log.txt'))
