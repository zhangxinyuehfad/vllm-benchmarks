from re import L
from typing import Union
from pathlib import Path
from handler import DataHandler

from data import ServingDataEntry, LatencyDataEntry, ThroughputDataEntry, data_prc


data_handler = DataHandler()

def fetch_pr_from_es(index_name: str = None):
    sources = data_handler.search_data_from_vllm('vllm_benchmark_throughput', source=True)
    print(sources)
    return sources

def prc_json_to_es(folder_path: Union[str, Path]):
    data_instance = data_prc(folder_path=folder_path)
    return data_instance

if __name__ == '__main__':

    res = fetch_pr_from_es()
    for k,v in res.items():
        print(f"{k}:{v}")