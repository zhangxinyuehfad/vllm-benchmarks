from handler import DataHandler
from common import VLLM_SCHEMA


data_handler = DataHandler()

for index in VLLM_SCHEMA:
    data_handler.index_name = index
    data_handler.delete_id_list_with_bulk_insert(['3217f0d10fbbc6e6cc8b0db9594b8cef515b4f90_Meta-Llama-3-8B-Instruct'])