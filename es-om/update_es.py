from venv import create
from numpy import source
from handler import DataHandler


datahandler = DataHandler()

index_name = 'vllm_benchmark_throughput'
items =  datahandler.search_data_from_vllm(index_name, source=True)
for data in items['hits']['hits']:
    _id = data['_id']
    print(_id)
    _source = data['_source']
    created_at = _source.get('created_at',None)
    if created_at:
        datahandler.update_data_for_exist_id(index_name, _id, {"model_name":"Meta-Llama-3-8B-Instruct"})