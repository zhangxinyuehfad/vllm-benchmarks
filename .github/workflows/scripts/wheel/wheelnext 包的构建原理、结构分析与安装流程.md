[TOC]



# 1 使用 variantlib 生成变体包

本章以原始包 [vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64.whl](https://files.pythonhosted.org/packages/3f/7d/476715c5ee86812a2c8e09be4dd4f7adabed40dd605f71a2c4282cc7a84e/vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64.whl) 为例，详述如何通过注入变体信息 ascend :: npu_type :: 910b 生成变体包 vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64-a2.whl，以便更好理解变体包内部结构的变化及产生变化的内容来源

## 1.1 安装 uv-wheelnext

**参考文档：**[An experimental, variant-enabled build of uv](https://astral.sh/blog/wheel-variants)

```shell
# 执行以下命令安装
$ curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_DOWNLOAD_URL=https://wheelnext.astral.sh sh

# 执行以下命令刷新 PATH 环境变量
$ source $HOME/.local/bin/env

# 查看版本号，可以发现命令仍为 uv，但版本已经带有 uv-wheelnext
$ uv --version
uv-wheelnext 0.8.4
```



## 1.2 安装 variantlib 工具

```shell
# 克隆 variantlib 源代码
$ git clone https://github.com/wheelnext/variantlib.git

# 进入克隆的 variantlib 源代码目录
$ cd variantlib

# 创建虚拟环境
$ uv venv

# 安装 variantlib
$ uv pip install --system .

# 查看版本号，确认安装是否成功
$ variantlib --version
variantlib version: 0.0.3
```



## 1.3 生成变体包

### 1.3.1 准备 pyproject.toml 文件

编写 pyproject.toml 文件（必须）：

```toml
[variant.default-priorities]
namespace = ["ascend"]

[variant.providers.ascend]
enable-if = "platform_system == 'Linux'"
plugin-api = "huawei_ascend_variant_provider.plugin:AscendVariantPlugin"
requires = ["huawei-ascend-variant-provider>=0.0.1,<1.0.0"]
```



关于 pyproject.toml 文件，有以下几点注意：

- 文件名称可以随意命名，不必须为 pyproject.toml
- variantlib 在注入变体信息过程中，只是读取 pyproject.toml，并不会对其修改
- **该 pyproject.toml 文件与 vllm_ascend 项目本身的 pyproject.toml  并无关联**，因此有两种用法：
  - 新建 pyproject.toml（可任意命名），只需写入以上的 variant 信息即可
  - 在 vllm_ascend 项目原有的 pyproject.toml 中追加 variant 信息



### 1.3.2 生成变体包

执行以下命令，注入变体信息，生成变体包：

```shell
$ variantlib make-variant \
    -f vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64.whl \
    -o ./ \
    --pyproject-toml pyproject.toml \
    --property "ascend :: npu_type :: 910b" \
    --variant-label a2 \
    --skip-plugin-validation
```



执行以下命令，校验变体包属性：

```shell
$ variantlib analyze-wheel \
    -i vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64-a2.whl 
variantlib.commands.analyze_wheel - INFO - Filepath: `vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64-a2.whl` ... is a Wheel Variant - Label: `a2`
############################## Variant: `38edb458` #############################
ascend :: npu_type :: 910b
################################################################################
```



`variantlib make-variant` 命令相关选项及作用如下：

| 命令选项                   | 作用                                   |
| -------------------------- | -------------------------------------- |
| `-f`                       | 指定基础 wheel 包                      |
| `-o`                       | 指定输出变体包的位置                   |
| `--pyproject-toml`         | 指定包含 variant 信息的 pyproject.toml |
| `--property`               | 指定变体特征                           |
| `--variant-label`          | 指定变体包的变体后缀，如 -a2、-a3      |
| `--skip-plugin-validation` | 跳过使用 provider 校验                 |



# 2 原始包与变体包的结构分析

根据第 1 章的操作，成功构建出变体包 vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64-a2.whl，以下将通过拆包对比的方法，分析注入变体信息过程中，产生了哪些变化以及变化的来源

## 2.1 原始包与变体包名称差异

原始包名称：`vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64.whl`

变体包名称：`vllm_ascend-0.13.0rc1-cp311-cp311-manylinux_2_24_x86_64-a2.whl`

对比这两个包的名称可以发现，变体包多了一个变体后缀 `-a2`。关于变体后缀，参考以下说明：

- **来源：** 有以下两种来源（参考代码：`variantlib/api.py:347-364`）
  - 由 `variantlib make-variant` 命令的 `--variant-label`  选项指定
  - 若没有指定，则根据变体属性计算 SHA256 取前 8 位作为 label
- **作用：** 用于判断指定的包是否为变体包（参考代码：`variantlib/commands/analyze_wheel.py:54-64`）
  - 若变体后缀存在，则认为该包为变体包
  - 若变体后缀不存在，则认为该包为普通包



## 2.2 原始包与变体包结构差异

使用 `unzip` 命令分别解压原始包与变体包，查看其结构差异

原始包的结构如下：

```
.
├── vllm_ascend
│   ├── ascend_config.py
│   ├── ......
│   └── xlite
└── vllm_ascend-0.13.0rc1.dist-info
    ├── entry_points.txt
    ├── LICENSE
    ├── METADATA
    ├── RECORD
    ├── top_level.txt
    └── WHEEL

20 directories, 20 files
```



变体包的结构如下：

```
.
├── vllm_ascend
│   ├── ascend_config.py
│   ├── ......
│   └── xlite
└── vllm_ascend-0.13.0rc1.dist-info
    ├── entry_points.txt
    ├── LICENSE
    ├── METADATA
    ├── RECORD
    ├── top_level.txt
    ├── variant.json
    └── WHEEL

20 directories, 21 files
```



对比原始包与变体包结构发现，在变体包的 .dist-info 目录下多出一个 variant.json 文件。关于该文件，有以下信息（参考代码：`variantlib/commands/make_variant.py:241-287`）：

- 该文件在注入变体信息，构建变体包时产生

- 与其他文件相同，该文件的 SHA256 值同样会被记录到 .dist-info/RECORD 文件中

  ```
  vllm_ascend-0.13.0rc1.dist-info/variant.json,sha256=3LE9xShDUHoYkI1LktyD3Dq4n0JJLM5U_DSM_DQajrg,624
  ```

- 除该文件及 .dist-info/RECORD 文件之外，其他文件完全不变

- 该文件的内容来源参考以下 2.3 节

## 2.3 variant.json 文件内容的来源

查看 variant.json 文件内容：

```json
{
    "$schema": "https://variants-schema.wheelnext.dev/v0.0.3.json",
    "default-priorities": {
        "namespace": [
            "ascend"
        ]
    },
    "providers": {
        "ascend": {
            "enable-if": "platform_system == 'Linux'",
            "plugin-api": "huawei_ascend_variant_provider.plugin:AscendVariantPlugin",
            "requires": [
                "huawei-ascend-variant-provider>=0.0.1,<1.0.0"
            ]
        }
    },
    "variants": {
        "a2": {
            "ascend": {
                "npu_type": [
                    "910b"
                ]
            }
        }
    }
}
```



该文件的内容来源及作用如下（参考代码：`variantlib/api.py:173-272`）：

- **`$schema`：**
  - 来源：硬编码常量 `VARIANTS_JSON_SCHEMA_URL`
  - 作用：
    - 标明该 variant.json 文件遵循的是 wheelnext 变体规范的 v0.0.3 版本，便于工具（如 uv-wheelnext）根据版本号正确解析
    - 支持 JSON Schema 的编辑器或工具可以据此自动校验 variant.json 的结构是否合法
- **`default-priorities`：**
  - 来源：`variantlib make-variant` 命令 `--pyproject-toml` 选项指定的 [pyproject.tom](#1.3.1-准备-pyproject.toml-文件) 文件。若该文件没有包含 `[variant.*]` 配置信息，则字段值为空
  - 作用（参考代码：`variantlib/resolver/sorting.py`）： 
    - 控制变体候选的排序优先级，列表中靠前的 namespace 优先级更高
    - 安装时，包管理器通过 provider 插件获取当前平台支持的属性后，用此优先级对可用变体排序，选出最佳匹配

- **`providers`：**
  - 来源：与 `default-priorities` 相同
  - 作用： 定义如何加载和调用 provider 插件来获取当前平台的变体属性（参考代码：`variantlib/plugins/loader.py`）
    - `enable-if`：环境标记表达式，安装时评估此条件决定是否加载该插件
    - `plugin-api`：插件的导入路径（如 `module:ClassName`），用于动态加载插件实例
    - `requires`：该插件的依赖包列表，安装时需要先确保这些依赖可用
- **`variants`**：
  - 来源：
    - **`key`：** 与变体包的变体后缀一致，参考 [2.1 原始包与变体包名称差异](#2.1-原始包与变体包名称差异)
    - **`value`：** 按 `namespace → feature → [values]` 嵌套的属性字典，由 `variantlib make-variant` 命令的 `--property` 选项指定
  - 作用：声明该包所有已构建的变体组合及其属性值（参考代码：`variantlib/resolver/filtering.py`）
    - 安装时，将每个变体的属性与当前平台（通过 provider 插件查询到的）支持的属性做匹配过滤
    - 多个属性间是 AND 关系（必须全部满足），单个属性的多个 value 间是 OR 关系（满足任一即可）
    - 过滤后的变体再按 `default-priorities` 排序，选出最优变体安装



# 3 uv-wheelnext 如何识别安装变体包



待补充......
