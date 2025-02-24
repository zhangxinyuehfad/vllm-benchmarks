from operator import ge
from pathlib import Path
import turtle


def get_all_commit(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            commit_id= line.strip().split()[0]
            print(f"{commit_id}")

if __name__ == '__main__':
    get_all_commit('/Users/wangli/vllm-ascend/commit_log.txt')
