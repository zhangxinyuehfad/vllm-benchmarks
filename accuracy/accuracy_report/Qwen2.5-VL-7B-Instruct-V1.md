# Qwen2.5-VL-7B-Instruct
**vLLM Version**: vLLM: 0.9.1 ([b6553be](https://github.com/vllm-project/vllm/commit/b6553be)), **vLLM Ascend**: main ([0e43813](https://github.com/vllm-project/vllm-ascend/commit/0e43813))
**Software Environment**: CANN: 8.1.RC1, PyTorch: 2.5.1, torch-npu: 2.5.1.post1.dev20250619  
**Hardware Environment**: Atlas A2 Series  
**Datasets**: mmmu_val  
**vLLM Engine**: V1  
**Parallel Mode**: TP
**Execution Mode**: aclgraph
**Command**:  
```bash
export MODEL_ARGS='pretrained=Qwen/Qwen2.5-VL-7B-Instruct,max_model_len=8192,dtype=auto,tensor_parallel_size=2,max_images=2'
lm_eval --model vllm-vlm --model_args $MODEL_ARGS --tasks mmmu_val \ 
--apply_chat_template --fewshot_as_multiturn  --batch_size 1
```
  
| Task                  | Filter | n-shot | Metric   | Value   | Stderr |
|-----------------------|-------:|-------:|----------|--------:|-------:|
| mmmu_val                              | none   | 0      | acc    | ✅0.5156 | ± 0.0162 |
<details>
<summary>mmmu_val details</summary>

| Task                  | Filter | n-shot | Metric   | Value   | Stderr |
|-----------------------|-------:|-------:|----------|--------:|-------:|
| mmmu_val                              | none   | 0      | acc    | ✅0.5156 | ± 0.0162 |
| - Art and Design                      | none   | 0      | acc    | 0.6667 | ± 0.0424 |
| - Art                                 | none   | 0      | acc    | 0.6667 | ± 0.0875 |
| - Art Theory                          | none   | 0      | acc    | 0.8333 | ± 0.0692 |
| - Design                              | none   | 0      | acc    | 0.6667 | ± 0.0875 |
| - Music                               | none   | 0      | acc    | 0.5000 | ± 0.0928 |
| - Business                            | none   | 0      | acc    | 0.4200 | ± 0.0406 |
| - Accounting                          | none   | 0      | acc    | 0.4333 | ± 0.0920 |
| - Economics                           | none   | 0      | acc    | 0.5333 | ± 0.0926 |
| - Finance                             | none   | 0      | acc    | 0.3667 | ± 0.0895 |
| - Manage                              | none   | 0      | acc    | 0.3333 | ± 0.0875 |
| - Marketing                           | none   | 0      | acc    | 0.4333 | ± 0.0920 |
| - Health and Medicine                 | none   | 0      | acc    | 0.5933 | ± 0.0404 |
| - Basic Medical Science               | none   | 0      | acc    | 0.6000 | ± 0.0910 |
| - Clinical Medicine                   | none   | 0      | acc    | 0.6000 | ± 0.0910 |
| - Diagnostics and Laboratory Medicine | none   | 0      | acc    | 0.4667 | ± 0.0926 |
| - Pharmacy                            | none   | 0      | acc    | 0.6667 | ± 0.0875 |
| - Public Health                       | none   | 0      | acc    | 0.6333 | ± 0.0895 |
| - Humanities and Social Science       | none   | 0      | acc    | 0.6917 | ± 0.0419 |
| - History                             | none   | 0      | acc    | 0.7000 | ± 0.0851 |
| - Literature                          | none   | 0      | acc    | 0.8000 | ± 0.0743 |
| - Psychology                          | none   | 0      | acc    | 0.7333 | ± 0.0821 |
| - Sociology                           | none   | 0      | acc    | 0.5333 | ± 0.0926 |
| - Science                             | none   | 0      | acc    | 0.4133 | ± 0.0408 |
| - Biology                             | none   | 0      | acc    | 0.4000 | ± 0.0910 |
| - Chemistry                           | none   | 0      | acc    | 0.3667 | ± 0.0895 |
| - Geography                           | none   | 0      | acc    | 0.4667 | ± 0.0926 |
| - Math                                | none   | 0      | acc    | 0.4000 | ± 0.0910 |
| - Physics                             | none   | 0      | acc    | 0.4333 | ± 0.0920 |
| - Tech and Engineering                | none   | 0      | acc    | 0.4143 | ± 0.0341 |
| - Agriculture                         | none   | 0      | acc    | 0.5000 | ± 0.0928 |
| - Architecture and Engineering        | none   | 0      | acc    | 0.4667 | ± 0.0926 |
| - Computer Science                    | none   | 0      | acc    | 0.4000 | ± 0.0910 |
| - Electronics                         | none   | 0      | acc    | 0.3333 | ± 0.0875 |
| - Energy and Power                    | none   | 0      | acc    | 0.2667 | ± 0.0821 |
| - Materials                           | none   | 0      | acc    | 0.4333 | ± 0.0920 |
| - Mechanical Engineering              | none   | 0      | acc    | 0.5000 | ± 0.0928 |
</details>
