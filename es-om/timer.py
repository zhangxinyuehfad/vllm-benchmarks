from datetime import datetime, timedelta
from operator import index
import pytz
import subprocess

from handler import DataHandler
from db import get_es_schema


def get_datetime(day: int=0):
    """
    Get datetime of `day` days ago from today in ISO format.
    """
    shanghai_tz = pytz.timezone("Asia/Shanghai")
    now_shanghai = datetime.now(shanghai_tz)  
    days_ago = now_shanghai - timedelta(days=day)  
    return str.split(days_ago.isoformat(), "+")[0]


def update_all_schema_time(commit_id: str=None, created_at: str=None):
    schemas = get_es_schema()
    dataHandler = DataHandler()
    for schema in schemas:
        dataHandler.index_name = schema
        data_list = dataHandler.search_data_from_vllm(schema, source=True)['hits']['hits']
        print(f"in schema: {schema}")
        for data in data_list:
            _id = data['_id']
            source = data['_source']
            created_at = source.get('created_at', None)
            print(f"id:{_id}, created_at:{created_at}")
            if created_at:
                dataHandler.update_data_for_exist_id(_id, {"created_at": get_datetime()})



id_to_delete = ['94cd66bba7b8e90a4b00eb92649b1239aabf3780', 
                'ee43179767ba1a61be543ed42beca276bee061eb', 
                'fd18ae649453fa4c31b58b04ba75d3fd9ed0b3d4',
                '6042c210bc715573a65c76209445a3d92054c1a6',
                'c131e43e7d5983b394d6846de432b3a0d7031935',
                '1715230867048aaf3102dbe6448b3c476db74c9e',
                '14bca9911a265bb3c75708dbd4fcdfe56d267db4',
                'b64ee7d346511b6ea7a64b09db58c17aa1c915ef'
                ]

data_handler = DataHandler()
data_handler.index_name = 'vllm_benchmark_serving'

data_list = data_handler.get_field_value(data_handler.index_name, ['commit_id', 'created_at', 'commit_title'])
for data in data_list:
    commit_id = data.get('commit_id', None)
    print(data)
    if commit_id:
        result = subprocess.run(
            ["git", '-C', '/Users/wangli/vllm-ascend', "show", "-s", "--format=%cd", commit_id, "--date=iso-strict"],
            capture_output=True, text=True
        )
        created_at = result.stdout.strip()
        created_at = str.split(created_at, "+")[0]
        print(created_at)
        data_handler.update_data_for_exist_id(index_name=data['_index'], id=data['_id'], data={'created_at': created_at})