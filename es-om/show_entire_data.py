from handler import DataHandler
from common import VLLM_SCHEMA


data_handler = DataHandler()
for schema in VLLM_SCHEMA:
    res = data_handler.search_data_from_vllm(schema, source=True)
    print(schema)
    res = res['hits']['hits']
    for r in res:
        print(r['_id'])
        print(r['_source'].get('created_at', None))
        print(r['_source'].get('commit_title', None))
    print()
