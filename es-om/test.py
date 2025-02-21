from re import S
import requests
from datetime import datetime, timedelta
import random, string, hashlib

from handler import DataHandler


data_handler = DataHandler()
data_handler.index_name = 'vllm_serving_test_3'

# data_handler.add_single_data(commit_id, data_to_insert.to_dict())
# data_handler.delete_index('vllm_serving_test_3')
# sdata_handler.update_data_for_exist_id('jM6mR39k', {"Model":"updated_data"})
resp =  data_handler.search_data_from_vllm()
data = resp["hits"]["hits"]

for _id in data:
     print(_id["_id"])
     print(_id)