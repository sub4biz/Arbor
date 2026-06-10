<p align="center">
  <img src="assets/hero.svg" alt="Arbor — Optimize anything" width="100%">
</p>

<p align="center">
  <em>Toward Generalist Autonomous Research via Hypothesis-Tree Refinement</em>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="assets/arbor_paper.pdf"><img src="https://img.shields.io/badge/Paper-PDF-B31B1B?style=for-the-badge" alt="Paper"></a>
  <a href="https://github.com/RUC-NLPIR/Arbor"><img src="https://img.shields.io/badge/Code-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://RUC-NLPIR.github.io/Arbor/"><img src="https://img.shields.io/badge/Project_Page-Live-0E9B9B?style=for-the-badge&logo=githubpages&logoColor=white" alt="Project Page"></a>
  <a href="https://RUC-NLPIR.github.io/Arbor/docs/"><img src="https://img.shields.io/badge/Docs-Material-526CFE?style=for-the-badge&logo=materialformkdocs&logoColor=white" alt="Docs"></a>
</p>

<p align="center">
  <b>English</b> | <a href="README.zh-CN.md">简体中文</a>
</p>

**Arbor is an autonomous research agent that turns a long-horizon objective into a
cumulative search.** Give it a benchmark and a goal; it proposes hypotheses, edits
code, runs real experiments, learns from the results, and keeps the improvements that
hold up on held-out data. Instead of one-shot attempts that forget what failed, Arbor
grows a **hypothesis tree**: every idea becomes a branch — pruned if it fails,
harvested if it works — and insights propagate back so later ideas start smarter.

Arbor runs **two cooperating agents**:

- **Coordinator** — the research director. It maintains the Idea Tree, drives the
  search via the *arbor cycle*, and dispatches experiments.
- **Executor** — the research engineer. Given one idea, it faithfully implements the
  code changes, runs the experiment in an isolated git worktree, and reports evidence.

<table>
<tr><td><b>Grows evidence, not logs</b></td><td>Results, failure modes, and distilled insights are preserved in a persistent Idea Tree — not lost in a scrollback buffer.</td></tr>
<tr><td><b>Held-out discipline by default</b></td><td>Executors iterate on a dev split; only improvements that clear a configurable margin on a held-out test split are merged. No overfitting to the metric you optimize.</td></tr>
<tr><td><b>Isolated, reversible experiments</b></td><td>Every experiment runs in its own git worktree on a dedicated branch. Your <code>main</code> branch is never touched until you merge.</td></tr>
<tr><td><b>Backpropagated insight</b></td><td>After each experiment, an LLM abstracts what was learned and pushes it up the tree, so sibling and descendant ideas inherit hard-won context.</td></tr>
<tr><td><b>Built for real experiments</b></td><td>Long-running training and evaluation are first-class: generous wall-clock timeouts, partial-metric recovery on timeout, and optional staged budgets (smoke → pilot → full).</td></tr>
<tr><td><b>Use any model</b></td><td>Anthropic, OpenAI / Responses API, or anything OpenAI-compatible through LiteLLM (DeepSeek, Gemini, Qwen, vLLM, Ollama, local gateways). Reasoning traces are preserved when the backend exposes them.</td></tr>
<tr><td><b>Live dashboard + read-only WebUI</b></td><td>A terminal UI shows the tree, branch budgets, current action, token usage, and inline Q&A. A read-only WebUI mirrors the run at <code>127.0.0.1:8765</code>.</td></tr>
<tr><td><b>Human-in-the-loop when you want it</b></td><td>Run fully autonomous, or pause at ideation and before each experiment to steer direction — without polluting the Coordinator's context.</td></tr>
<tr><td><b>Domain adaptation without code changes</b></td><td>A one-line <code>plugin:</code> retargets the agent (e.g. Kaggle/MLE mode) via a single YAML; Skills are markdown playbooks loaded on demand.</td></tr>
</table>

---

## Install

**Requirements:** Python ≥ 3.10 and Git.

```bash
git clone https://github.com/RUC-NLPIR/Arbor.git
cd Arbor
pip install -e .          # or: uv pip install -e .
```

That's it — `pip install -e .` installs Arbor and the `arbor` command into the current
Python environment. We recommend a virtual environment so it stays isolated:

```bash
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -e .
```

### Verify

```bash
arbor version
arbor doctor      # checks PATH, venv leakage, git, and API keys
```

### Optional: a global `arbor` command with pipx

If you'd rather have `arbor` available in **every** directory without activating a venv,
install it with [pipx](https://pipx.pypa.io) instead — it manages the isolated
environment for you:

```bash
pipx install -e .          # run from the cloned Arbor directory
pipx reinstall research-agent   # upgrade later
```

> Seeing `arbor: command not found`? It usually means it was installed into a venv
> that isn't active or on your `PATH`. Run `arbor doctor` for a diagnosis, activate the
> right environment, or use the pipx install above.

### Documentation

Full documentation — installation, configuration, the method, the CLI reference, plugins,
and skills — lives in [`docs/`](docs/index.md) and builds into a documentation site:

```bash
pip install -e ".[docs]"   # install docs dependencies
mkdocs serve               # live preview at http://127.0.0.1:8000
```

---

## Getting Started

```bash
arbor setup       # one-time: configure provider / model / base_url / API key
arbor             # start an interactive session in the current directory
arbor doctor      # diagnose the install
```

`arbor setup` writes `~/.arbor/config.yaml`, so day-to-day you can just run `arbor`
with no flags. The first thing Arbor does is an **intake conversation** that turns your
goal, target directory, metric, baseline, budget, dev/test discipline, and artifact
paths into a one-screen **Arbor Research Contract**. Once you confirm it, the live
dashboard takes over.

```bash
# Point at a benchmark directory and a config
arbor --cwd ./benchmark --config research_config.yaml

# Give an initial goal up front; intake refines the rest
arbor "improve validation score without touching the test split" --cwd ./benchmark

# Small dry run
arbor --cwd ./benchmark --config research_config.yaml --max-cycles 3
```

During a run you can type `/status`, `/tree`, `/evidence`, `/branches`, `/cost`,
`/pause`, `/resume`, `/report`, or `/abort`.

### Prepare a benchmark

Your target directory should have:

- a runnable evaluation script (e.g. `run_eval.py`),
- evaluation data (ideally a **dev** split and a held-out **test** split), and
- a clean git repository (no uncommitted changes).

A minimal `research_config.yaml`:

```yaml
# LLM/API live in `arbor setup`; project config is usually just the task and budget.
task: >
  Optimize the agent's accuracy on the benchmark.
  Do NOT modify the evaluation harness or data files.

coordinator:
  max_cycles: 10          # arbor cycles to explore
  max_depth: 2            # Idea Tree depth
  merge_threshold: 5.0    # min held-out % gain to merge into trunk
  ui:
    interaction_mode: review   # auto | direction | review | collaborative

executor:
  max_turns: 100
```

A copy-pasteable example with every option lives in
[`examples/research_config.example.yaml`](examples/research_config.example.yaml).

---

## How It Works

### The arbor cycle

Each cycle runs six steps:

```
① OBSERVE   analyze current results and failure modes
② IDEATE    propose 1–3 new ideas from the analysis and tree insights
③ SELECT    pick the highest-priority idea to test
④ DISPATCH  run an Executor on it in an isolated git worktree
⑤ BACKPROP  record the result; abstract the insight up to ancestor nodes
⑥ DECIDE    continue / merge into trunk / prune / stop
```

### The Idea Tree

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

- **Depth 0 (Root):** the research objective and global insights.
- **Depth 1:** research directions (paper-title-level ideas).
- **Depth 2+:** concrete methods, implemented and tested by Executors.

### Git strategy

```
main (never touched, always clean)
  └── research/run_xxx/trunk            (accumulated, verified improvements)
       ├── research/run_xxx/1.1/...     (experiment branch)
       ├── research/run_xxx/1.2/...     (experiment branch)
       └── ...
```

Each Executor works in its own worktree. Verified improvements merge into `trunk`; you
merge `trunk` back into `main` when you're satisfied:

```bash
git log research/run_xxx/trunk --oneline   # review every improvement
git merge research/run_xxx/trunk           # promote into main
```

### Evaluation discipline

- **Dev split** — used for day-to-day iteration; Executors evaluate here.
- **Test split** — used only before merging into trunk and in the final report, to
  guard against overfitting.

### Human-in-the-loop

`ui.interaction_mode` controls how much you steer a run:

| Mode | Behavior |
| --- | --- |
| `auto` | Fully autonomous. |
| `direction` | At ideation, Arbor summarizes evidence and candidate axes, then asks you where to go next. |
| `review` | Pauses before writing a node to the tree and before each Executor starts. |
| `collaborative` | `direction` + `review`. |

When the Coordinator pauses, your input opens an **isolated discussion** with a
read-only companion — multi-turn, and it never pollutes the Coordinator's main
context. Override on the fly with `arbor run ... --interaction-mode collaborative`.

---

## Configuration

LLM access is configured once with `arbor setup` and stored in `~/.arbor/config.yaml`.
There is a single unified `provider` field:

| `provider` | Use it for | Reasoning trace |
| --- | --- | --- |
| `anthropic` | Native Anthropic (with prompt caching) | thinking signature blocks |
| `openai` | Native OpenAI / any OpenAI-compatible Responses API endpoint (default) | encrypted reasoning |
| `litellm` | Unified transport: DeepSeek / Gemini / Qwen / vLLM / any OpenAI-compatible proxy | preserved when the backend exposes it |

```yaml
# DeepSeek-R1 via LiteLLM
provider: litellm
model: deepseek/deepseek-reasoner

# Self-hosted vLLM / Ollama chat gateway
provider: litellm
model: Qwen/Qwen2.5-72B-Instruct
base_url: http://localhost:8000/v1

# GPT-5 / Copilot-style gateway (Responses API)
provider: openai
model: gpt-5
base_url: http://localhost:4141/v1
api_key: dummy
```

API keys can come from the environment (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) or from
`arbor setup` / the YAML `api_key` field (handy for local proxies). See
[`examples/research_config.example.yaml`](examples/research_config.example.yaml) for the
full set of options.

---

## CLI Reference

Day to day you only need `arbor`. The lower-level commands remain for debugging and
legacy flows.

| Command | What it does |
| --- | --- |
| `arbor` | Start an interactive research session (defaults to `arbor run`). |
| `arbor run ...` | Explicitly start a research run. |
| `arbor report <session>` | Regenerate `REPORT.md` for a previous session. |
| `arbor setup` | Configure provider / model / keys → `~/.arbor/config.yaml`. |
| `arbor config init/show/path` | Manage the user config file. |
| `arbor doctor` | Diagnose install, PATH, git, and API keys. |
| `arbor version` | Print the installed version. |
| `run-research` | Lower-level wrapper around the Coordinator with full logging and dashboards. |
| `coordinator` | Run the Coordinator directly. |
| `executor` | Run a single Executor against one idea. |
| `review-research` | Browse and re-render past runs and dashboards. |

---

## Plugins & Skills

A single line retargets the agent to a new domain — evaluation protocol, protected
data directories, required outputs, and timeout presets all come from the plugin:

```yaml
plugin: mle_kaggle   # switches to Kaggle/MLE mode
```

A plugin is one YAML file (prompt-injection points + config overrides + profiles +
lifecycle hooks + an eval contract); a Skill is a markdown playbook the agent loads on
demand at runtime. A copy-pasteable Kaggle config lives in
[`examples/kaggle_config.example.yaml`](examples/kaggle_config.example.yaml).

---

## Output & Resume

A run writes a session directory containing `REPORT.md`, `events.jsonl`,
`run_stats.json`, the Idea Tree, and per-experiment artifacts:

```bash
ls .arbor/sessions/                       # find the latest session
arbor report .arbor/sessions/<run_name>   # re-render its report
```

Runs are resumable — interrupt with `Ctrl+C` any time and continue later:

```bash
run-research --cwd ./project --config research_config.yaml            # first run
run-research --cwd ./project --config research_config.yaml --resume   # continue
```

On resume, Arbor loads `idea_tree.json` (written atomically on every change), resets any
interrupted `running` node to `pending`, and continues from the tree's current state.

---

## Results

Arbor was evaluated as a single controller across model training, harness engineering,
and data synthesis — only the material, objective, evaluator, and budget change. It
wins the held-out test on all six tasks against strong single-agent baselines.

| Task | Direction | Initial | Codex | Claude Code | **Arbor** | Gain |
| --- | --- | --- | --- | --- | --- | --- |
| Optimizer Design | steps ↓ | 3325 | 3325 | 3287.5 | **3237.5** | +2.63% |
| Architecture Design | loss ↓ | 1.098 | 1.083 | 1.033 | **1.028** | +6.38% |
| Terminal-Bench 2.0 | pass ↑ | 69.81 | 73.59 | 71.70 | **77.36** | +7.55 |
| BrowseComp | acc ↑ | 45.33 | 50.00 | 53.33 | **67.67** | +22.34 |
| Search-Agent Data | gap ↑ | 5.00 | 9.00 | 12.00 | **18.00** | +13.0 |
| Math-Reasoning Data | gap ↑ | 1.04 | 6.25 | 8.33 | **20.83** | +19.79 |

On **MLE-Bench Lite** with GPT-5.5, Arbor reaches **86.36% Any-Medal** (100% valid
submissions, 95.45% above median, 77.27% gold). See the [paper](assets/arbor_paper.pdf)
for full protocols and ablations.

---

## Project Structure

The code lives in `src/` and is imported as the `research_agent` package.

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

## Citation

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

Built at the Gaoling School of Artificial Intelligence, Renmin University of China, and
Microsoft Research.
