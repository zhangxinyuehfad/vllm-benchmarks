#!/bin/bash

# 参数设置
INPUT_LEN=32
OUTPUT_LEN=128
BATCH_SIZE=8
NUM_ITERS_WARMUP=5
NUM_ITERS=15
DEVICE="npu"

# 如果有七个设备，这里要改为7
TENSOR_PARALLEL_SIZE=1 

# 模型列表
MODELS=("/root/.cache/modelscope/hub/LLM-Research/Meta-Llama-3-8B-Instruct")

# 输出结果的JSON文件名前缀
OUTPUT_JSON_PREFIX="lcg_latency_results"

# 开始测试
for MODEL_NAME in "${MODELS[@]}"; do
    echo "Running latency test for model: $MODEL_NAME"
    
    # 设置输出JSON文件名
    OUTPUT_JSON="${OUTPUT_JSON_PREFIX}.json"
    
    # 执行延迟测试并将结果保存到文件和终端输出
    python3 benchmark_latency.py \
        --model $MODEL_NAME \
        --batch-size $BATCH_SIZE \
        --input-len $INPUT_LEN \
        --output-len $OUTPUT_LEN \
        --num-iters-warmup $NUM_ITERS_WARMUP \
        --tensor-parallel-size $TENSOR_PARALLEL_SIZE \
        --num-iters $NUM_ITERS \
    
done

echo "All latency tests completed."