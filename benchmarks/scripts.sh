#!/bin/bash

# parameters
test_name="throughput_telechat2_tp1"
model="/root/.cache/modelscope/hub/LLM-Research/Meta-Llama-3-8B-Instruct"
tensor_parallel_size=1
load_format="dummy"
dataset="/root/wl/datasets/sharegpt_v3_unfiltered_cleaned_split/ShareGPT_V3_unfiltered_cleaned_split.json"
num_prompts=200
backend="vllm"
trust_remote_code=True
max_model_len=None

# command
python ../benchmarks/benchmark_throughput.py \
  --model $model \
  --tensor_parallel_size $tensor_parallel_size \
  --load_format $load_format \
  --dataset $dataset \
  --num_prompts $num_prompts \
  --backend $backend \
  --trust_remote_code 