#
# Copyright (c) 2025 Huawei Technologies Co., Ltd. All Rights Reserved.
# This file is a part of the vllm-ascend project.
# Adapted from vllm-project/blob/main/tests/entrypoints/llm/test_accuracy.py
# Copyright 2023 The vLLM team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import gc
import json
import multiprocessing
import sys
import time

import lm_eval
import torch

UNIMODAL_MODEL_NAME = ["Qwen/Qwen2.5-7B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"]
UNIMODAL_TASK = ["ceval-valid", "mmlu", "gsm8k"]
# UNIMODAL_TASK = ["mmlu"]
MULTIMODAL_NAME = ["Qwen/Qwen2.5-VL-7B-Instruct"]
MULTIMODAL_TASK = ["mmmu_val"]
#MULTIMODAL_TASK = ["mmmu_accounting"]

def run_accuracy_unimodal(queue, model=None, dataset=None):
    try:
        model_args = f"pretrained={model},max_model_len=4096,dtype=auto,tensor_parallel_size=2,gpu_memory_utilization=0.6"
        results = lm_eval.simple_evaluate(
            model="vllm",
            model_args=model_args,
            tasks=dataset,
            apply_chat_template=True,
            fewshot_as_multiturn=True,
            batch_size=1,
            num_fewshot=5,
        )
        print(f"Success: {model} on {dataset}")
        measured_value = results["results"]
        queue.put(measured_value)
    except Exception as e:
        print(f"Error in run_accuracy_unimodal: {e}")
        queue.put(e)
        sys.exit(1) 
    finally:
        torch.npu.empty_cache()
        gc.collect()

def run_accuracy_multimodal(queue, model=None, dataset=None):
    try:
        model_args = f"pretrained={model},max_model_len=8192,dtype=auto,tensor_parallel_size=2,max_images=2"
        results = lm_eval.simple_evaluate(
            model="vllm-vlm",
            model_args=model_args,
            tasks=dataset,
            apply_chat_template=True,
            fewshot_as_multiturn=True,
            batch_size=1,
        )
        print(f"Success: {model} on {dataset}")
        measured_value = results["results"]
        queue.put(measured_value)
    except Exception as e:
        print(f"Error in run_accuracy_multimodal: {e}")
        queue.put(e)
        sys.exit(1)
    finally:
        torch.npu.empty_cache()
        gc.collect()

def generate_md(model_name, tasks_list):
    header = (
        "|                 Tasks                 |Version|Filter|n-shot|Metric|   |Value |   |Stderr|\n"
        "|---------------------------------------|------:|------|-----:|------|---|-----:|---|-----:|"
    )
    rows = []
    for task_dict in tasks_list:
        for key, stats in task_dict.items():
            alias = stats.get("alias", key)
            task_name = alias.strip()
            indent = len(alias) - len(alias.lstrip(" "))
            version = 1 if indent >= 2 else 2

            metric_key = None
            for k in stats:
                if "," in k and not k.startswith("acc_stderr"):
                    metric_key = k
                    break
            if metric_key is None:
                continue
            metric, flt = metric_key.split(",", 1)

            value = stats[metric_key]
            stderr = stats.get(f"{metric}_stderr,{flt}", 0)
            if model_name in UNIMODAL_MODEL_NAME:
                n_shot = "5"
            else:
                n_shot = "0"
            row = (
                f"| {task_name:<37} | {version:6d} | {flt:<6} | {n_shot:6} | {metric:<6} |↑  | {value:5.4f} |±  | {stderr:5.4f}|"
            )
            rows.append(row)
    md = header + "\n" + "\n".join(rows)
    print(md)
    return md

def safe_md(args, accuracy):
    print("accaurcy:", accuracy)
    data = json.loads(json.dumps(accuracy))
    for model_key, tasks_list in data.items():
        md_content = generate_md(model_key, tasks_list)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"create Markdown file:{args.output}")


def main(args):
    accuracy = {}
    accuracy[args.model] = []
    result_queue: Queue[float] = multiprocessing.Queue()
    if args.model in UNIMODAL_MODEL_NAME:
        for dataset in UNIMODAL_TASK:
            p = multiprocessing.Process(target=run_accuracy_unimodal, args=(result_queue, args.model, dataset))
            p.start()
            p.join()
            result = result_queue.get()
            print(result)
            accuracy[args.model].append(result)
    if args.model in MULTIMODAL_NAME:
        for dataset in MULTIMODAL_TASK:
            p = multiprocessing.Process(target=run_accuracy_multimodal, args=(result_queue, args.model, dataset))
            p.start()
            p.join()
            result = result_queue.get()
            print(result)
            accuracy[args.model].append(result)
    print(accuracy)
    safe_md(args, accuracy)
     
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--model', type=str, required=True)
    args = parser.parse_args()
    main(args)
