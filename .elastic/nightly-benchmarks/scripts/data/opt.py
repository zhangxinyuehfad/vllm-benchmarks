from handler import DataHandler
from common import VLLM_PULL_REQUEST_LIST


data_handler = DataHandler()

def fetch_pr_from_es(index_name: str):
    sources = data_handler.search_data_from_vllm(index_name)
    res = []
    print()
    for source in sources:
        commit_id = source['_id']
        data = source['_source']
        if data['need_test']:
            res.append({
                'commit_id':commit_id,
                'commit_title':data['commit_title'],
                'create_at': data.get('create_at', '')
            })
    return res

if __name__ == '__main__':
    data_handler.query_today(VLLM_PULL_REQUEST_LIST)
