from doctest import FAIL_FAST
import os
from cv2 import log
import requests
import json
import warnings
import re
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


logger = logging.getLogger()

ES_DOAMIN = os.getenv("ES_DOAMIN")
ES_AUTHORIZATION = os.getenv("ES_AUTHORIZATION")


class DataHandler():
    def __init__(self):
        self.headers = {
            "Content-Type": "application/x-ndjson",
            "Authorization": ES_AUTHORIZATION
        }
        self.domain = ES_DOAMIN
        self._index_name = "vllm_benchmarks"
        self.display_fields = []
        self.field_order = []
        self._create_at = "created_at"


    @property
    def create_at(self):
        """
        field_names: 查询表展示的选项 如果不存在则为空
        只影响展示表格的结果 不影响查询结果
        """
        return self._create_at

    @create_at.setter
    def create_at(self, value: list):
        self._create_at = value


    @property
    def index_name(self):
        """
        index_name: 查询的表名
        """
        return self._index_name


    @index_name.setter
    def index_name(self, value: str):
        self._index_name = value


    def create_table_with_property_type(self, property_type: dict):
        """
        创建表并设置字段类型
        不要改非float的字段 会出问题
        property_type: {"rank": {"type": "float"},
                        "star": {"type": "float"}}
        """
        try:
            data = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": property_type
                }
            }
            url = f"{self.domain}/{self._index_name}"
            resp = requests.put(
                url=url,
                headers=self.headers,
                data=json.dumps(data),
                verify=False
            )
            print(json.loads(resp.text))
        except Exception as e:
            logger.info(f"create table with property type error:\n{e}")


    def get_table_property_type(self):
        """
        用于检查表的property是否为数值类型
        """
        try:
            url = f"{self.domain}/{self._index_name}/_mapping"
            resp = requests.get(
                    url=url,
                    headers=self.headers,
                    verify=False
                )
            print(json.loads(resp.text))
        except Exception as e:
            logger.info(f"get table property type error:\n{e}")


    def delete_index(self, index_name):
        """
        慎用
        """
        try:
            url = f"{self.domain}/{index_name}"
            resp = requests.delete(
                    url=url,
                    headers=self.headers,
                    verify=False
                )
            print(json.loads(resp.text))
        except Exception as e:
            logger.info(f"delete table[{index_name}] error:\n{e}")


    def reindex(self, source_idx, dest_idx):
        """
        重命名表
        """
        data = {
            "source": {
                "index": source_idx
            },
            "dest": {
                "index": dest_idx
            }
        }
        url = f"{self.domain}/{self._index_name}"
        resp = requests.put(
                url=url,
                headers=self.headers,
                data=json.dumps(data),
                verify=False
            )
        print(json.loads(resp.text))


    def _format_query_items(self, query_items: dict):
        """
        格式化查询内容
        query_item = {'file_project': 'pytorch/pytorch'}的格式化数据为
        插入数据格式 此处只修改bool
        data = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'match_phrase': {
                                'file_project': {'query': 'pytorch/pytorch'}
                            }
                        }
                    ]
                }
            },
            'size': 5000,
            'sort': [{'Date': {'order': 'desc'}}]
        }
        """
        query_bool = {"bool": {}}
        must_list = list()
        if query_items:
            for k, v in query_items.items():
                must_list.append(
                    {
                        "match_phrase": {
                            k : {"query": v}
                        }
                    }
                )
        if must_list:
            query_bool["bool"].update({"must": must_list})
        return query_bool


    def _query_scroll_search(self, query_items=None, query_range=None):
        """
        scroll search
        query_items和query_range同时传入仅显示query_range结果
        """
        url = f"{self.domain}/{self._index_name}/_search?scroll=1m"
        data = {
            "query": {"match_all": {}},
            "size": 5000,
            # "sort": [
            #     {"Date": {"order": "desc"}},
            # ]
        }
        if query_items:
            query_bool = self._format_query_items(query_items)
            data["query"] = query_bool
        if query_range:
            data["query"].update(query_range)

        import pdb;pdb.set_trace()
        data = {
            'query': {
                'bool': {'must': [
                    {'match_phrase': {'file_project': {'query': 'vllm-project/vllm'}}},
                    {"range": {"Date": {"gte": "2024-12-01", "lte": "2025-01-01"}}}
                ]}
            },
            'size': 5000
        }

        try:
            resp = requests.get(
                url=url,
                headers=self.headers,
                data=json.dumps(data),
                verify=False
            )
            res_data = json.loads(resp.text)
            data_list = res_data["hits"]["hits"]
            scroll_id = res_data["_scroll_id"]
            scroll_list = ["no use"]  # while condition
            cnt = 0
            while scroll_id and len(scroll_list) != 0:
                cnt += 1
                logger.info(f"query {self._index_name} scroll num[{cnt}]")
                data = {
                    "scroll": "1m",
                    "scroll_id": scroll_id
                }
                resp = requests.get(
                    url=f"{self.domain}/_search/scroll",
                    headers=self.headers,
                    data=json.dumps(data),
                    verify=False
                )
                res_data = json.loads(resp.text)
                if not res_data["hits"]:
                    continue
                scroll_list = res_data["hits"]["hits"]
                scroll_id = res_data["_scroll_id"]
                data_list += scroll_list
        except Exception as e:
            raise Exception(f"{e}")
        return data_list


    def _qr_remove_create(self, source_list: list, create_show):
        try:
            source_list.remove(self.create_at)
        except:
            pass
        if create_show:
            source_list += [self.create_at]
        return source_list


    def _qr_get_table_field(self, field_names, create_show):
        """
        有时候不需要create_at
        """
        res: list = list()
        if not self.display_fields:
            res = self._qr_remove_create(field_names, create_show)
        else:
            self.display_fields = self._qr_remove_create(self.display_fields, create_show)
            # 根据self.display_fields剔除冗余项
            display_name: list = list()
            for name in field_names:
                if name in self.display_fields:
                    display_name.append(name)
            res = display_name

        return ["ID"] + res if create_show else res


    def _qr_get_record_order(self, field_names: list):
        try:
            res: list = list()
            for ele in self.field_order:
                # index能找到就找 找不到就pass
                try:
                    idx = field_names.index(ele)
                    res.append(idx)
                except:
                    pass
            return lambda x: tuple(x[i] for i in res)
        except Exception as e:
            raise Exception(f"record order process error {e}")


    def query_record(self, query_items=None, query_range=None, log_table=True, create_show=False):
        """
        查询表项
        query_items={"Type": "test"}
        query_range={"range": {"Date": {"gte": "2024-10-01", "lte": "2025-01-01"}}}
        log_table是否向日志文件中记录
        create_show是否显示create_at和ID项 主要用于raw数据插入
        """
        if not query_items:
            query_items = dict()

        data_list = self._query_scroll_search(query_items, query_range)
        if len(data_list) == 0:
            return None
        try:
            field_names = list(data_list[0]["_source"].keys())

            table = prettytable.PrettyTable()
            # table.field_names = self._qr_get_table_field(["ID"] + field_names, create_show)
            table.field_names = self._qr_get_table_field(field_names, create_show)
            all_record = []
            for ele in data_list:
                source_data = ele["_source"]
                # value_list = [ele["_id"]]  # 不要id了
                value_list = [ele["_id"]] if create_show else []
                for key in field_names:
                    if self.display_fields and key not in self.display_fields:
                        continue
                    if not create_show and key.startswith("create"):
                        continue
                    value_list.append(source_data.get(key, ""))

                all_record.append(value_list)

            # 排个序好对比
            if  self.field_order:
                all_record = sorted(
                    all_record,
                    key=self._qr_get_record_order(list(table.field_names))
                )
            for ele in all_record:
                table.add_row(ele)

            if log_table:
                logger.info(f"qury table record:\n{table}")
            return table
        except Exception as e:
            raise Exception(e)

    def search_data_from_vllm(self):
        url = f'{self.domain}/{self.index_name}/_search'
        data = {
            "_source": True,
            "size": 20,
            "query": {
            "match_all": {}
                },
            "sort": [
            { "create_at": { "order": "desc" } }  # 按时间倒序排序
        ]
        }
        resp =  requests.post(
            url=url,
            headers=self.headers,
            json=data,
            verify=False
        )
        # print(resp.json())
        return resp.json()
        

    def _format_data_for_bulk_insert(self, data_list):
        """
        data_list: [[data_id1, item1],[data_id2, item2]]
                   item = {"file_project": ...,
                           "Type": ...,}
        """
        if not data_list:
            return

        actions = ""
        for data in data_list:
            item = data[1]
            index_data = {
                "index": {
                    "_index": self._index_name,
                    "_id": data[0]
                }
            }
            actions += json.dumps(index_data) + "\n"
            actions += json.dumps(item) + "\n"
        return actions


    def add_single_data(self, id: str, data: dict):
        url = f'{self.domain}/{self.index_name}/_doc/{id}'
        header = self.headers.copy()
        header['Content-Type'] = 'application/json'
        try:
            resp = requests.put(
                url=url,
                headers=header,
                json=data,
                verify=False
            )
            resp.raise_for_status()
            logger.info(f'add data to {self.index_name}/{id} successful, Response: {resp.json()}')
        except requests.exceptions.RequestException as req_err:
            logger.error(f'failed to add data {req_err}', exc_info=True)
        except Exception as other_err:
            logger.error(f'failed to add data {other_err}', exc_info=True)

        

    def query_today(self):
        query = {
            "query": {
                "range": {
                    "create_at": {
                        "gte": "now/d",
                        "lt": "now+1d/d",
                        "time_zone": "+08:00"
                    }
                }
            }
        }
        url = f'{self.domain}/{self.index_name}/_search'
        header = self.headers.copy()
        header['Content-Type'] = 'application/json'
        try:
            resp = requests.post(url, header, query, verify=False)
            resp.raise_for_status()
            logger.info(f'search  successful')
            return resp.json()
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error during search: {req_err}", exc_info=True)

        except UnicodeEncodeError:
            logger.error("UnicodeEncodeError occurred while encoding data JSON", exc_info=True)
    
        except Exception as other_err:
            logger.error(f"Unexpected error during single search: {other_err}", exc_info=True)

    def update_data_for_exist_id(self, id: str, data: dict):
        url = f'{self.domain}/{self.index_name}/_update/{id}'
        header = self.headers.copy()
        header['Content-Type'] = 'application/json'
        update_data = {'doc':data}
        try:
            resp = requests.post(
                url, 
                headers=header, 
                json=update_data, 
                verify=False,
                )
            resp.raise_for_status()
            logger.info(f'update data {self.index_name}/{id} successful')
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error during update: {req_err}", exc_info=True)

        except UnicodeEncodeError:
            logger.error("UnicodeEncodeError occurred while encoding data JSON", exc_info=True)
    
        except Exception as other_err:
            logger.error(f"Unexpected error during single update: {other_err}", exc_info=True)


    def _bulk_insert(self, data_list: list):
        """
        数据插入总接口
        data_list: [[data_id1, item1],[data_id2, item2]]
                   item = {"file_project": ...,
                           "Type": ...,}
        """
        if not data_list:
            return
        interval = 1000
        n = int(len(data_list) / interval)
        if n <= 1:
            bulk_json = self._format_data_for_bulk_insert(data_list)
            self._put_bulk(bulk_json)
            return
        else:
            for i in range(n + 1):
                sub_list = data_list[i*interval:(i + 1)*interval]
                bulk_json = self._format_data_for_bulk_insert(sub_list)
                self._put_bulk(bulk_json)

    # 插入数据
    def _put_bulk(self, bulk_json):
        """
        调用ES API插入内容
        """
        if not bulk_json or bulk_json == "":
            return

        # logger.info(f"start insert data:\n{bulk_json.strip()}")
        try:
            resp = requests.post(
                self.domain + "/_bulk",
                data=bulk_json.encode("utf-8"),
                headers=self.headers,
                verify=False
            )
            logger.info(f"finish insert data:\n{resp.text}\n")
        except UnicodeEncodeError:
            bulk_json = bulk_json.encode("iso-8859-1", "ignore")
            resp = requests.put(
                url=self.domain,
                data=bulk_json,
                headers=self.headers
            )
            logger.info(f"UnicodeEncode finish insert data:\n{resp.text}")
        except Exception as otherError:
            logger.info(f"Insert Exception:\n{otherError}")


    def _data_insert_process_raw_data(self,
                                      all_lines,
                                      aim_field=None,
                                      dest_name=None):
        """
        插入原始数据不查重
        处理prettytable表形式的str结果
        """
        fields = all_lines[1].strip()[1:-1].split("|")
        fields = [f.strip() for f in fields]
        aim_idx = None
        try:
            aim_idx = fields.index(aim_field)
        except:  # 异常再刷成None
            aim_idx = None
        n = len(fields)
        data_list: list = list()
        for line in all_lines[3:]:
            if line.startswith("+-----") or line.strip() == "":
                continue

            values = line.strip()[1:-1].split("|")
            data_id = values[0].strip()
            # data_id = values[1].strip() + values[2].strip() + values[3].strip()
            item = {}
            for i in range(1, n):
                item[fields[i]] = values[i].strip()
                if aim_idx and aim_idx == i and dest_name:  # 批量修改某一项
                    item[fields[i]] = dest_name

            data_list.append([data_id, item])

        self._bulk_insert(data_list)


    def _get_lines_from_file(self, file_path):
        """
        file.readlines()
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()


    def data_insert_with_raw_data(self, file_path):
        """
        插入原始数据不查重
        修改查询后的数据表 直接通过file_path插入
        可给table新增某项内容一起插入
        use 'query_record()' table to insert
        """
        all_lines = self._get_lines_from_file(file_path)

        self._data_insert_process_raw_data(all_lines)


    def change_record_field(self, aim_item: dict, aim_field: str, dest_name: str):
        """
        查询aim_item数据 将所有Type的名字转为AIframework
        aim_item: {"Type": "traditionML"}
        aim_field: "Type"
        dest_name: "AIframework"
        """
        table = self.query_record(query_items=aim_item, log_table=False, create_show=True)
        logger.info(f"{self._index_name}: change [{aim_item}] to [{aim_field}/{dest_name}]")
        if not table or not table._rows:
            return
        table_list = str(table).split("\n")
        self._data_insert_process_raw_data(table_list, aim_field, dest_name)


    def _format_bulk_delete(self, id_lst):
        actions = ""
        for id in id_lst:
            index_data = {
                "delete": {
                    "_index": self._index_name,
                    "_id": id
                }
            }
            actions += json.dumps(index_data) + "\n"
        return actions


    def delete_id_list_with_bulk_insert(self, id_lst: list):
        """
        更快 只调用一次api
        """
        if not id_lst:
            return

        bulk_json = self._format_bulk_delete(id_lst)
        self._put_bulk(bulk_json)


    def _process_delete_resp(self, text: str):
        """
        简单判断查询是否成功
        """
        pattern = r'"total":(\d+),"deleted":(\d+),"batches":(\d+)'
        total, delete, batches = re.findall(pattern, text)[0]  # 一定有 不做异常处理 异常再说
        if delete != "0":
            return f'"total":{total},"deleted":{delete},"batches":{batches}'
        return False


    def _delete_by_query(self, query_items=None, all_clear=False):
        """
        _delete_by_query 删除总执行接口
        """
        if not all_clear and not query_items:
            print('need query_items to delete')
            return
        data = {
            "query": {}
        }

        if query_items:
            query_bool = self._format_query_items(query_items)
            data["query"].update(query_bool)

        if all_clear:
            data["query"] = {"match_all": {}}

        data = json.dumps(data)
        url = f"{self.domain}/{self._index_name}/_delete_by_query"
        try:
            resp = requests.post(
                url,
                data=data.encode("utf-8"),
                headers=self.headers,
                verify=False
            )
            processed_text = self._process_delete_resp(resp.text)
            if processed_text:
                logger.info(f"delete {processed_text}")
            else:
                logger.info(f"delete fail, id/query_items/all[{query_items}/{all_clear}]")
        except Exception as e:
            logger.info(f"Delete Exception: {e}")


    def delete_with_item(self, query_items: dict):
        self._delete_by_query(query_items=query_items)


    def delete_all_record(self):
        self._delete_by_query(all_clear=True)


  