import argparse
from tkinter import SE
from typing import Union, Dict, List

from handler import DataHandler
from timer import get_datetime
from data import data_prc, ServingDataEntry, LatencyDataEntry, ThroughputDataEntry

parser = argparse.ArgumentParser(description='add commit msg to es')

parser.add_argument('--commit_id', type=str, required=True)
parser.add_argument('--commit_title', type=str, required=True)


def send_data(data_instance: Dict[str, List[Union[ServingDataEntry, LatencyDataEntry, ThroughputDataEntry]]]):
    datahandler =  DataHandler()
    for index_name, data_list in data_instance.items():
        datahandler.index_name = index_name
        for data in data_list:
            insert_id = "_".join([data.commit_id, str(data.request_rate)]) if hasattr(data, 'request_rate') else data.commit_id
            datahandler.add_single_data(insert_id, data.to_dict())


if __name__ == '__main__':
    datahandler = DataHandler()
    datahandler.index_name = ("vllm_benchmark_serving")
    datahandler.update_data_for_exist_id('6042c210bc715573a65c76209445a3d92054c1a6_1.0', {'commit_title': '[CI] upgrade to newest pta (#187)'})
    