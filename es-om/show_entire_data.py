from handler import DataHandler
from common import VLLM_SCHEMA


data_handler = DataHandler()

id_list = []

for index in VLLM_SCHEMA:
    data_handler.index_name = index
    data = data_handler.search_data_from_vllm(index, source=True)
    for dl in  data['hits']['hits']:
        if dl['_source'].get('commit_id') == '3217f0d10fbbc6e6cc8b0db9594b8cef515b4f90':
            id_list.append(dl['_id'])

print(id_list)

for index in VLLM_SCHEMA:
    data_handler.index_name = index
    data_handler.delete_id_list_with_bulk_insert(id_lst=id_list)