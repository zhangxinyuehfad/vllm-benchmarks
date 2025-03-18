from numpy import source
from handler import DataHandler
from common import VLLM_SCHEMA


id_to_delete = ['12aa7115b58e6def5603e4eae6744f0af8e05634',
                '3217f0d10fbbc6e6cc8b0db9594b8cef515b4f90',
                '0db6670bfab8cb1d84c9e7270df0a1d42d6ce7ca'
                ]

ids = []

datahandler = DataHandler()
for schema in VLLM_SCHEMA:
    datahandler.index_name = schema
    doc = datahandler.search_data_from_vllm(schema, source=True)
    data = doc['hits']['hits']
    for value in data:
        _id = value['_id']
        _source = value['_source']
        commit_id = _source.get('commit_id', None)
        if commit_id in id_to_delete:
            ids.append(_id)
    print(ids)
    datahandler.delete_id_list_with_bulk_insert(ids)
    ids.clear()