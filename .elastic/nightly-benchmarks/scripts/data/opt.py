from re import L
from typing import Union
from pathlib import Path
from handler import DataHandler
from common import VLLM_PULL_REQUEST_LIST

from read_from_json import ServingDataEntry, LatencyDataEntry, ThroughputDataEntry, data_prc


data_handler = DataHandler()

def fetch_pr_from_es(index_name: str = None):
    sources = data_handler.search_data_from_vllm('vllm_benchmark_throughput', source=False)
    print(sources)
    return sources

def prc_json_to_es(folder_path: Union[str, Path]):
    data_instance = data_prc(folder_path=folder_path)
    return data_instance

if __name__ == '__main__':
    #res = prc_json_to_es('/Users/wangli/vllm-project/data/results')
    # for k,v in res.items():
    #     for data_entry in v:
    #         commit_id = data_entry.commit_id + ('_' + str(data_entry.request_rate) if hasattr(data_entry, 'request_rate') else '')
    #         data_handler.index_name = k
    #         print(k)
    #         print(commit_id)
    #         print(data_entry.to_dict())
    #         data_handler.add_single_data(commit_id, data_entry.to_dict())
    res = fetch_pr_from_es()
    for k,v in res.items():
        print(f"{k}:{v}")