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
    test_name: str
    pull_request: str
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






throuthput = ThroughputDataEntry(
    commit_id='12',
    test_name='llama3_8b',
    pull_request='sdaa',
    tp=1,
    created_at=None,
    requests_per_second=11.2,
    tokens_per_second=12.3
    )
print(throuthput.to_dict())