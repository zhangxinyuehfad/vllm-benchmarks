# Scripts 使用说明

本目录提供 `variantlib make-variant` 的批量执行封装。

能力概览：

- 基于 JSON 配置批量执行任务
- 支持按 `variant_label` 过滤
- 支持串行/并行执行
- 构建后自动校验产物
- 自动创建输出目录

## 文件说明

- `make_variant.py`: 批量执行脚本。
- `config.json`: 任务配置文件。
- `pyproject.toml`: `variantlib` 使用的插件/Provider 配置。

## 前置条件

- Python 3.11+
- 环境中可执行 `variantlib`
- 当前 Python 环境已安装脚本运行依赖

## 快速开始

### 1) 设置环境变量

Bash:

```bash
export WHEEL_FILE="path/to/input.whl"
export PROJECT_TOML="scripts/pyproject.toml"
export OUTPUT_DIR="./dist"
```

`WHEEL_FILE` 也可以指向目录；当 `wheel` 或 `wheel_env` 指向目录时，脚本会展开该目录下所有 `.whl` 文件，并按当前 job 配置分别执行。

### 2) 执行全部任务

```bash
python scripts/make_variant.py -c scripts/config.json
```

### 3) 先做 dry-run（推荐）

```bash
python scripts/make_variant.py -c scripts/config.json --dry-run
```

## 命令用法

### 必填参数

- `-c`, `--config`: 配置 JSON 路径

### 常用可选参数

- `-l`, `--variant-label`: 按标签筛选任务，可重复传入或逗号分隔
- `--dry-run`: 只打印命令，不实际执行
- `-j`, `--jobs`: 并行 worker 数，默认 `1`

### 示例

只执行一个标签：

```bash
python scripts/make_variant.py -c scripts/config.json -l a2
```

执行两个标签：

```bash
python scripts/make_variant.py -c scripts/config.json -l 310p,a3
```

并行执行：

```bash
python scripts/make_variant.py -c scripts/config.json -j 3
```

## 当前仓库默认配置说明

当前 `scripts/config.json` 默认包含：

- `variables`: 定义环境变量名（`WHEEL_FILE`、`PROJECT_TOML`、`OUTPUT_DIR`）
- `jobs`: 3 个任务，标签分别为 `310p`、`a2`、`a3`

默认配置未设置 `variables.variant_label_aliases`，因此 `-l` 过滤应直接使用任务标签（例如 `a2`）。

## 配置结构（`config.json`）

脚本期望配置是一个 JSON 对象，包含 `variables` 和 `jobs`。

### `variables`

- `wheel_env` (string): 输入 wheel 路径对应的环境变量名
- `pyproject_toml_env` (string): pyproject 路径对应的环境变量名
- `output_dir_env` (string): 输出目录对应的环境变量名
- `wheel` (string, optional): 默认输入 wheel 路径
- `pyproject_toml` (string, optional): 默认 pyproject 路径
- `output_dir` (string, optional): 默认输出目录
- `variant_label_aliases` (object, optional): 标签映射（源标签 -> 目标标签）

### `jobs[]`

每个任务支持：

- `variant_label` (string, 推荐)
- `property` (string) 或 `properties` (string 数组)
- `null_variant` (bool)
- `wheel` (string)
- `wheel_env` (string)
- `pyproject_toml` (string)
- `pyproject_toml_env` (string)
- `output_dir` (string)
- `output_dir_env` (string)
- `skip_plugin_validation` (bool)
- `no_isolation` (bool)
- `installer` (`pip` 或 `uv`)

规则：

- `property/properties` 与 `null_variant=true` 互斥
- `wheel`、`pyproject_toml`、`output_dir` 支持 job 覆盖 `variables` 默认值
- 当对应字段未配置时，会从 `*_env` 指定的环境变量读取
- `wheel` 可以是单个 `.whl` 文件或目录；目录模式会展开其中所有 `.whl` 文件

## 构建后校验行为

单个任务命令成功后，脚本会校验：

- 输出 wheel 文件存在
- 输出文件名是合法的 wheel variant 文件名
- 若 job 设置了 `variant_label`，文件名中的标签必须一致
- wheel 的 dist-info 中存在 `variant-dist-info.json`
- wheel 中实际属性与任务配置属性一致

## 输出目录行为

任务执行前：

- 如果输出目录不存在，会自动创建
- 如果输出路径存在但不是目录，会报错并标记该任务失败

## 常见问题排查

### `No matching jobs for --variant-label`

- 检查 `-l` 传入值是否和配置中的 `variant_label` 一致
- 如果使用别名，确认已在 `variables.variant_label_aliases` 配置映射

### 报 `Job #x is missing required field`

- 确认 job、`variables`、环境变量中至少有一处提供了必需字段
- 常见必需项：`wheel`、`pyproject_toml`、`output_dir`

### 运行脚本时报 `ModuleNotFoundError`

- 在当前 Python 环境安装所需依赖
- 如果是源码环境运行，确认导入路径设置正确

### 配置解析报错

- 检查 JSON 格式是否合法
- 确保 `variables` 是对象
- 确保 `jobs` 是非空数组

## 最小端到端示例

```bash
export WHEEL_FILE="dist/vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64.whl"
export PROJECT_TOML="scripts/pyproject.toml"
export OUTPUT_DIR="dist"

python scripts/make_variant.py -c scripts/config.json --dry-run -l a2
python scripts/make_variant.py -c scripts/config.json -l a2
```
