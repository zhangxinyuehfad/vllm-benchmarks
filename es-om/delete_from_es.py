from tkinter.tix import Tree
from handler import DataHandler


id_to_delete = ['fd18ae649453fa4c31b58b04ba75d3fd9ed0b3d4', 'ee43179767ba1a61be543ed42beca276bee061eb', '94cd66bba7b8e90a4b00eb92649b1239aabf3780']

data_handler = DataHandler()

data_handler.index_name = 'vllm_benchmark_throughput'
print(data_handler.search_data_from_vllm('vllm_benchmark_throughput', source=True))

