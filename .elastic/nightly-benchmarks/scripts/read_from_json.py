from dataclasses import dataclass, asdict
from pathlib import Path
from sys import flags
from typing import List, Optional, Dict, Union
import os
import json
from datetime import datetime
from argparse import ArgumentParser

from pandas import read_json



cli_parser = ArgumentParser()


@dataclass
class BaseDataEntry:
    commit_id: str
    commit_title: str
    test_name: str
    tp: int
    created_at: Union[str, None]

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ServingDataEntry(BaseDataEntry):
    mean_ttft_ms: float
    median_ttft_ms: float
    p99_ttft_ms: float
    mean_tpot_ms: float
    p99_tpot_ms: float
    median_tpot_ms: float
    mean_itl_ms: float
    median_itl_ms: float
    p99_itl_ms: float
    std_ttft_ms: float
    std_tpot_ms: float
    std_itl_ms: float
    request_rate: int


# Throughput
@dataclass
class ThroughputDataEntry(BaseDataEntry):
    requests_per_second: float
    tokens_per_second: float

# Latency
@dataclass
class LatencyDataEntry(BaseDataEntry):
    mean_latency: float
    median_latency: float
    percentile_99: float

# @dataclass
# class PerformanceDataSet:
#     serving_data: List[ServingDataEntry] = []
#     throughput_data: List[ThroughputDataEntry] = []
#     latency_data: List[LatencyDataEntry] = []

#     def add_serving_data(self, entry: ServingDataEntry):
#         self.serving_data.append(entry)

#     def add_throughput_data(self, entry: ThroughputDataEntry):
#         self.throughput_data.append(entry)

#     def add_latency_data(self, entry: LatencyDataEntry):
#         self.latency_data.append(entry)


#     def from_cli_args(self):
#         RESULT_PATH = os.path.join(get_project_root(), "benchmarks", "results")
#         if not os.path.isdir(RESULT_PATH):
#             raise FileNotFoundError(f"the path {RESULT_PATH} do not exist")

#         for json_file in Path(RESULT_PATH).rglob('*.json'):
#             try:
#                 data_map = self.read_json(json_file)
#                 test_name = Path(json_file).stem
#                 if str.startswith('latency'):
#                     avg_latency = data_map[avg_latency]
#                     percentiles = data_map[percentiles]
#                     self.add_latency_data(LatencyDataEntry())
#                 if str.startswith('serving'):
#                     pass
#                 if str.startswith('throuthput'):
#                     pass
#             except Exception as e:
#                 print(f"read from {json_file} error: {e}")


#     @staticmethod
#     def add_cli_args(parser: ArgumentParser) -> ArgumentParser:
#         parser.add_argument("--commit_id", type=str)
#         parser.add_argument("--pull_request", type=str)

#     @staticmethod
#     def read_json(file_path: Union[Path, str]) -> Dict:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data_dict = json.loads(f)
#         return data_dict





def get_project_root() -> Path:
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / '.git').exists() or (current_path / 'setup.py').exists():
            return current_path
        current_path = current_path.parent
    return current_path


def read_from_json(file_path: Union[str, Path]):

    with open(file_path, 'r') as f:
        data = json.load(f)
    return data



RESULT_PATH = os.path.join(get_project_root(), "benchmarks","results")
print(RESULT_PATH)

data = read_from_json("/Users/wangli/vllm-project/vllm-benchmarks/.elastic/nightly-benchmarks/tests/latency-tests.json")

print(data)
print(type(data))