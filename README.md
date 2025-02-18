This repo is created to run  benchmark scripts for npu, developers can easily run performance tests on their own machines with one line of code .
### How to use
#### Prerequisites
- Please make sure that you have vllm and vllm-ascned installed and npu environment，cause these scripts are specially prepared for npu devices
- To speed up the script， you can download the models and datasets to your local computer in advance and change the path in the json file in the .elastic/nightly-benchmarks/tests folder
#### Run benchmarks
these scripts can automatically conduct performance testing of serving, through and latency, run the following command:
```
cd vllm-ascend
bash .elastic/nightly-benchmarks/scripts/run-performance-benchmarks.sh
```
once  the script is finished, you can view the result files in the benchmarks/results folder. and the results may looks like below:
```
|-- latency_llama8B_tp1.json
|-- serving_llama8B_tp1_sharegpt_qps_1.json
|-- serving_llama8B_tp1_sharegpt_qps_16.json
|-- serving_llama8B_tp1_sharegpt_qps_4.json
|-- serving_llama8B_tp1_sharegpt_qps_inf.json
|-- throughput_llama8B_tp1.json
```