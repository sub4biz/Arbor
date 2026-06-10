<p align="center">
  <img src="assets/hero.svg" alt="Arbor — Optimize anything" width="100%">
</p>

<p align="center">
  <em>面向通用自主科研的假设树精炼方法（Toward Generalist Autonomous Research via Hypothesis-Tree Refinement）</em>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="assets/arbor_paper.pdf"><img src="https://img.shields.io/badge/Paper-PDF-B31B1B?style=for-the-badge" alt="Paper"></a>
  <a href="https://github.com/RUC-NLPIR/Arbor"><img src="https://img.shields.io/badge/Code-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://RUC-NLPIR.github.io/Arbor/"><img src="https://img.shields.io/badge/Project_Page-Live-0E9B9B?style=for-the-badge&logo=githubpages&logoColor=white" alt="Project Page"></a>
  <a href="https://RUC-NLPIR.github.io/Arbor/docs/"><img src="https://img.shields.io/badge/Docs-Material-526CFE?style=for-the-badge&logo=materialformkdocs&logoColor=white" alt="Docs"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <b>简体中文</b>
</p>

**Arbor 是一个自主科研智能体，它把一个长周期目标转化为持续累积的搜索过程。** 给它一个基准
（benchmark）和一个目标；它会提出假设、修改代码、运行真实实验、从结果中学习，并保留那些在
留出（held-out）数据上确实站得住脚的改进。不同于"一次性尝试、转头就忘"的做法，Arbor 会生长出
一棵**假设树**：每个想法都是一根分支——失败就剪枝，成功就收获——而洞见会反向传播，让后来的想法
从更聪明的起点出发。

Arbor 由**两个协作的智能体**组成：

- **Coordinator（协调者）** —— 科研总监。它维护想法树（Idea Tree），通过 *arbor cycle*（Arbor 循环）
  驱动搜索，并派发实验。
- **Executor（执行者）** —— 科研工程师。给定一个想法，它忠实地实现代码改动，在隔离的 git worktree 中
  运行实验，并汇报证据。

<table>
<tr><td><b>沉淀证据，而非日志</b></td><td>结果、失败模式与提炼出的洞见会保存在持久化的想法树中——不会淹没在滚动缓冲区里。</td></tr>
<tr><td><b>默认的留出纪律</b></td><td>Executor 在 dev 划分上迭代；只有在留出 test 划分上跨过可配置阈值的改进才会被合并。绝不对你优化的指标过拟合。</td></tr>
<tr><td><b>隔离、可回退的实验</b></td><td>每个实验都在自己的 git worktree、独立分支上运行。在你主动合并之前，<code>main</code> 分支绝不会被触碰。</td></tr>
<tr><td><b>反向传播的洞见</b></td><td>每次实验后，由 LLM 抽象出"学到了什么"并上推到树中，让同辈与后代想法继承来之不易的上下文。</td></tr>
<tr><td><b>为真实实验而生</b></td><td>长时间的训练与评测是一等公民：宽裕的墙钟超时、超时后的部分指标恢复，以及可选的分阶段预算（smoke → pilot → full）。</td></tr>
<tr><td><b>任意模型</b></td><td>Anthropic、OpenAI / Responses API，或任何通过 LiteLLM 接入的 OpenAI 兼容后端（DeepSeek、Gemini、Qwen、vLLM、Ollama、本地网关）。当后端暴露推理轨迹时会被保留。</td></tr>
<tr><td><b>实时仪表盘 + 只读 WebUI</b></td><td>终端 UI 展示想法树、分支预算、当前动作、token 用量以及内联问答。只读 WebUI 在 <code>127.0.0.1:8765</code> 镜像整个运行过程。</td></tr>
<tr><td><b>需要时随时人在回路</b></td><td>可完全自主运行，也可在构思阶段以及每个实验开始前暂停以引导方向——而不会污染 Coordinator 的上下文。</td></tr>
<tr><td><b>无需改代码的领域适配</b></td><td>一行 <code>plugin:</code> 即可把智能体切换到新领域（如 Kaggle/MLE 模式），全部来自一个 YAML；Skill 则是按需加载的 markdown 操作手册。</td></tr>
</table>

---

## 安装

**环境要求：** Python ≥ 3.10 与 Git。

```bash
git clone https://github.com/RUC-NLPIR/Arbor.git
cd Arbor
pip install -e .          # 或：uv pip install -e .
```

就这样——`pip install -e .` 会把 Arbor 及 `arbor` 命令安装进当前 Python 环境。我们建议使用
虚拟环境以保持隔离：

```bash
python -m venv .venv && source .venv/bin/activate   # 可选但推荐
pip install -e .
```

### 验证

```bash
arbor version
arbor doctor      # 检查 PATH、venv 泄漏、git 与 API key
```

### 可选：用 pipx 安装全局 `arbor` 命令

如果你希望在**任意**目录都能直接用 `arbor` 而无需激活 venv，可改用
[pipx](https://pipx.pypa.io) 安装——它会替你管理隔离环境：

```bash
pipx install -e .          # 在克隆下来的 Arbor 目录中执行
pipx reinstall research-agent   # 之后升级
```

> 遇到 `arbor: command not found`？通常是因为它被装进了一个未激活、或不在 `PATH` 上的 venv。
> 运行 `arbor doctor` 做诊断、激活正确的环境，或改用上面的 pipx 安装。

### 文档

完整文档——安装、配置、方法、CLI 参考、插件与技能——位于 [`docs/`](docs/index.md)，并可构建成
一个文档站点：

```bash
pip install -e ".[docs]"   # 安装文档依赖
mkdocs serve               # 在 http://127.0.0.1:8000 实时预览
```

---

## 快速上手

```bash
arbor setup       # 一次性：配置 provider / model / base_url / API key
arbor             # 在当前目录启动一次交互式会话
arbor doctor      # 诊断安装
```

`arbor setup` 会写入 `~/.arbor/config.yaml`，于是日常你只需直接运行 `arbor`、无需任何参数。
Arbor 启动后做的第一件事是一次**接入对话（intake）**：把你的目标、目标目录、指标、基线、预算、
dev/test 纪律以及产物路径，整理成一屏的 **Arbor 研究契约（Research Contract）**。一经你确认，
实时仪表盘便接管全程。

```bash
# 指向一个基准目录与一份配置
arbor --cwd ./benchmark --config research_config.yaml

# 一开始就给出目标；intake 会把其余部分补全
arbor "improve validation score without touching the test split" --cwd ./benchmark

# 小规模试跑
arbor --cwd ./benchmark --config research_config.yaml --max-cycles 3
```

运行过程中你可以输入 `/status`、`/tree`、`/evidence`、`/branches`、`/cost`、
`/pause`、`/resume`、`/report` 或 `/abort`。

### 准备一个基准

你的目标目录应当包含：

- 一个可运行的评测脚本（如 `run_eval.py`），
- 评测数据（最好有 **dev** 划分与留出的 **test** 划分），以及
- 一个干净的 git 仓库（没有未提交改动）。

一份最小的 `research_config.yaml`：

```yaml
# LLM/API 在 `arbor setup` 里配置；项目配置通常只放任务与预算。
task: >
  Optimize the agent's accuracy on the benchmark.
  Do NOT modify the evaluation harness or data files.

coordinator:
  max_cycles: 10          # 探索的 arbor 循环数
  max_depth: 2            # 想法树深度
  merge_threshold: 5.0    # 合并入主干所需的最小留出提升（%）
  ui:
    interaction_mode: review   # auto | direction | review | collaborative

executor:
  max_turns: 100
```

一份包含全部选项、可直接复制的示例见
[`examples/research_config.example.yaml`](examples/research_config.example.yaml)。

---

## 工作原理

### Arbor 循环（the arbor cycle）

每个循环执行六个步骤：

```
① OBSERVE   分析当前结果与失败模式
② IDEATE    基于分析与树中洞见，提出 1–3 个新想法
③ SELECT    选出优先级最高的想法去验证
④ DISPATCH  在隔离的 git worktree 中派一个 Executor 去做
⑤ BACKPROP  记录结果；把洞见抽象上推到祖先节点
⑥ DECIDE    继续 / 合并入主干 / 剪枝 / 停止
```

### 想法树（the Idea Tree）

```
ROOT (baseline: 20%)
├── 1: Retrieval optimization        [insight: "retrieval quality is the bottleneck"]
│   ├── 1.1: Constraint decomposition + verification   [40%, merged]
│   ├── 1.2: Periodic re-read injection                [40%, pruned — no net gain]
│   └── 1.3: Answer-extraction tuning                  [35%, pruned]
├── 2: Multi-perspective search      [insight: "search scaffolding hurts here"]
│   └── 2.1: Breadth-first search                      [25%, pruned]
└── 3: Code-level intervention       [insight: "code-level > prompt-level"]
    ├── 3.1: Continuation injection                    [70%, merged]
    └── 3.2: ANSWER-tag extraction                     [45%, done]
```

- **深度 0（根）：** 研究目标与全局洞见。
- **深度 1：** 研究方向（论文标题级别的想法）。
- **深度 2+：** 具体方法，由 Executor 实现并测试。

### Git 策略

```
main (never touched, always clean)
  └── research/run_xxx/trunk            (accumulated, verified improvements)
       ├── research/run_xxx/1.1/...     (experiment branch)
       ├── research/run_xxx/1.2/...     (experiment branch)
       └── ...
```

每个 Executor 都在自己的 worktree 中工作。已验证的改进合并进 `trunk`；当你满意时，再把
`trunk` 合并回 `main`：

```bash
git log research/run_xxx/trunk --oneline   # 审阅每一项改进
git merge research/run_xxx/trunk           # 提升进 main
```

### 评测纪律

- **Dev 划分** —— 用于日常迭代；Executor 在此评测。
- **Test 划分** —— 仅在合并入主干之前以及最终报告中使用，以防止过拟合。

### 人在回路（Human-in-the-loop）

`ui.interaction_mode` 控制你对一次运行的引导程度：

| 模式 | 行为 |
| --- | --- |
| `auto` | 完全自主。 |
| `direction` | 在构思阶段，Arbor 汇总证据与候选方向，然后问你下一步往哪走。 |
| `review` | 在向树写入节点之前、以及每个 Executor 启动之前暂停。 |
| `collaborative` | `direction` + `review`。 |

当 Coordinator 暂停时，你的输入会开启一段与只读伴随智能体的**隔离讨论**——支持多轮，且绝不会
污染 Coordinator 的主上下文。可临时用 `arbor run ... --interaction-mode collaborative` 覆盖。

---

## 配置

LLM 访问只需用 `arbor setup` 配置一次，存放在 `~/.arbor/config.yaml`。只有一个统一的
`provider` 字段：

| `provider` | 适用于 | 推理轨迹 |
| --- | --- | --- |
| `anthropic` | 原生 Anthropic（带 prompt 缓存） | thinking signature 块 |
| `openai` | 原生 OpenAI / 任何 OpenAI 兼容的 Responses API 端点（默认） | 加密推理 |
| `litellm` | 统一传输层：DeepSeek / Gemini / Qwen / vLLM / 任何 OpenAI 兼容代理 | 后端暴露时予以保留 |

```yaml
# 通过 LiteLLM 接入 DeepSeek-R1
provider: litellm
model: deepseek/deepseek-reasoner

# 自托管的 vLLM / Ollama chat 网关
provider: litellm
model: Qwen/Qwen2.5-72B-Instruct
base_url: http://localhost:8000/v1

# GPT-5 / Copilot 风格网关（Responses API）
provider: openai
model: gpt-5
base_url: http://localhost:4141/v1
api_key: dummy
```

API key 可来自环境变量（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`），也可来自 `arbor setup`
或 YAML 的 `api_key` 字段（对本地代理很方便）。完整选项见
[`examples/research_config.example.yaml`](examples/research_config.example.yaml)。

---

## CLI 参考

日常你只需 `arbor`。更底层的命令保留用于调试与旧流程。

| 命令 | 作用 |
| --- | --- |
| `arbor` | 启动交互式科研会话（默认等同 `arbor run`）。 |
| `arbor run ...` | 显式启动一次科研运行。 |
| `arbor report <session>` | 为之前的会话重新生成 `REPORT.md`。 |
| `arbor setup` | 配置 provider / model / key → `~/.arbor/config.yaml`。 |
| `arbor config init/show/path` | 管理用户配置文件。 |
| `arbor doctor` | 诊断安装、PATH、git 与 API key。 |
| `arbor version` | 打印已安装版本。 |
| `run-research` | 围绕 Coordinator 的底层封装，带完整日志与仪表盘。 |
| `coordinator` | 直接运行 Coordinator。 |
| `executor` | 针对单个想法运行一个 Executor。 |
| `review-research` | 浏览并重新渲染过往运行与仪表盘。 |

---

## 插件与技能（Plugins & Skills）

一行即可把智能体切换到新领域——评测协议、受保护的数据目录、必需产物以及超时预设，全部来自
该插件：

```yaml
plugin: mle_kaggle   # 切换到 Kaggle/MLE 模式
```

插件是**一个 YAML 文件**（prompt 注入点 + 配置覆盖 + profiles + 生命周期钩子 + 一份评测契约）；
技能（Skill）是智能体在运行时按需加载的 **markdown 操作手册**。一份可直接复制的 Kaggle 配置见
[`examples/kaggle_config.example.yaml`](examples/kaggle_config.example.yaml)。

---

## 输出与续跑（Output & Resume）

一次运行会写出一个会话目录，包含 `REPORT.md`、`events.jsonl`、`run_stats.json`、想法树以及
每个实验的产物：

```bash
ls .arbor/sessions/                       # 找到最近的会话
arbor report .arbor/sessions/<run_name>   # 重新渲染其报告
```

运行可续跑——随时用 `Ctrl+C` 中断，之后继续：

```bash
run-research --cwd ./project --config research_config.yaml            # 首次运行
run-research --cwd ./project --config research_config.yaml --resume   # 继续
```

续跑时，Arbor 会加载 `idea_tree.json`（每次变更都原子写入），把任何被中断的 `running` 节点
重置为 `pending`，并从树的当前状态继续。

---

## 实验结果

Arbor 被作为**单一控制器**，跨模型训练、harness 工程与数据合成进行评测——仅改变材料、目标、
评测器与预算。在全部六项任务上，它都在留出 test 上胜过强单智能体基线。

| 任务 | 方向 | 初始 | Codex | Claude Code | **Arbor** | 增益 |
| --- | --- | --- | --- | --- | --- | --- |
| Optimizer Design | steps ↓ | 3325 | 3325 | 3287.5 | **3237.5** | +2.63% |
| Architecture Design | loss ↓ | 1.098 | 1.083 | 1.033 | **1.028** | +6.38% |
| Terminal-Bench 2.0 | pass ↑ | 69.81 | 73.59 | 71.70 | **77.36** | +7.55 |
| BrowseComp | acc ↑ | 45.33 | 50.00 | 53.33 | **67.67** | +22.34 |
| Search-Agent Data | gap ↑ | 5.00 | 9.00 | 12.00 | **18.00** | +13.0 |
| Math-Reasoning Data | gap ↑ | 1.04 | 6.25 | 8.33 | **20.83** | +19.79 |

在 **MLE-Bench Lite**（GPT-5.5）上，Arbor 达到 **86.36% Any-Medal**（100% 有效提交、95.45%
高于中位、77.27% 金牌）。完整协议与消融见[论文](assets/arbor_paper.pdf)。

---

## 项目结构

代码位于 `src/`，以 `research_agent` 包的形式导入。

```
src/                 # the `research_agent` package
├── core/            Shared infrastructure: ReAct loop, tools, LLM providers, context mgmt
├── executor/        Executor agent + `executor` CLI
├── coordinator/     Coordinator agent, Idea Tree, orchestrator, coordinator tools
├── cli/             `arbor` CLI: intake, live dashboard, setup, doctor, config
├── events/          Typed event bus and payloads
├── report/          Report generation
├── webui/           Read-only run-monitoring web server
├── plugins/         Domain plugins (e.g. mle_kaggle.yaml)
├── skills/          On-demand markdown playbooks
├── dashboard.py     HTML dashboard generator
├── run.py           `run-research` CLI
└── review.py        `review-research` CLI
```

---

## 引用

```bibtex
@misc{jin2026arbor,
  title  = {Toward Generalist Autonomous Research via Hypothesis-Tree Refinement},
  author = {Jiajie Jin and Yuyang Hu and Kai Qiu and Qi Dai and Chong Luo and
            Guanting Dong and Xiaoxi Li and Tong Zhao and Xiaolong Ma and
            Gongrui Zhang and Zhirong Wu and Bei Liu and Zhengyuan Yang and
            Linjie Li and Lijuan Wang and Hongjin Qian and Yutao Zhu and Zhicheng Dou},
  year   = {2026},
  note   = {Living technical report}
}
```

---

由中国人民大学高瓴人工智能学院与微软研究院共同打造。
