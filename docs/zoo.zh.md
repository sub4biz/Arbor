# 基准库 —— 格式参考

这一页讲一个基准文件夹的确切格式,以及 `arbor benchmark verify` 检查什么。整体介绍见
[总览](zoo-overview.md)。

格式是**文档优先**的:一个基准就是一个文档齐全的文件夹。README 是 Arbor 在 intake 时读的自然语言
说明——**没有要填的 YAML 清单**。

## 一个基准文件夹包含什么

每个 `arbor-zoo/<name>/` 里有四样东西:

| 文件 / 目录 | 作用 | 面向 |
| --- | --- | --- |
| `README.md` | 任务是什么、指标、Arbor 能改什么、dev/test 怎么分——用自然语言写。 | Arbor(和人) |
| 基线代码 | 可编辑的基线——`solution.py`,或一整套文件。 | Arbor 编辑 |
| `eval.sh` *或* `eval.py` | 受保护 eval 入口。`bash eval.sh dev\|test`(或 `python eval.py --split …`)打印一行 `score: <float>`。 | 受保护 |
| `PROVENANCE.md` | 来源、环境、baseline 怎么实现、污染评估、注意事项。 | 人看 |
| `data/`、`task.py`… | eval 需要的数据 / ground-truth(受保护)。 | — |

以 `_` 开头的文件夹(如 `_template`)是脚手架,会被跳过。

### `README.md` —— 用大白话写清任务

README 就是 Arbor 用来理解任务的东西,跟它 intake 读任何 repo 一样。怎么读着顺就怎么写;一个基准
通常写清四件事:

1. **任务** —— 是什么、一个解长什么样。
2. **指标** —— eval 打印什么(一行 `score:`)、越大还是越小好。
3. **Arbor 能改什么** —— 基线文件;其余一切(eval、ground-truth、数据)不许碰。
4. **dev / test** —— 两者怎么分,让留出集清楚(不相交的种子,或 `data/dev/` vs `data/test/`)。

格式里**没有固定的 baseline 数字**:同一份基线在不同硬件/模型上跑出来不一样,所以它写在 PROVENANCE
里,而不是钉成一个值。

### `PROVENANCE.md` —— 给人看的卡片

必含章节(校验器会查在不在):**Source**、**Setup & environment**、**Baseline**、
**Contamination assessment**、**Caveats**。来源、license、baseline 怎么实现的(以及分数波动多大)、
留出集的理由,都写在这里给维护者读。

## `arbor benchmark verify` 查什么

`verify` 是个轻量的**结构**检查——查齐全,不查正确性,也**不跑 eval**(baseline 分数本就不通用)。
它查:

- `README.md` 在、且非空;
- `PROVENANCE.md` 在、且必含章节齐全;
- eval 入口(`eval.sh` 或 `eval.py`)在。

```bash
arbor benchmark verify arbor-zoo/<name>   # 缺东西就非零退出
arbor benchmark list arbor-zoo            # 列出有哪些基准
```

dev/test 是否*真的*留出、baseline 到底干了什么,写在 PROVENANCE 文字里、由人判断——不做机器强制。

## 用 Arbor 跑一个基准

Arbor 在仓库根的 git worktree 里跑实验,所以请在 Arbor 检出**之外**的副本里工作:

```bash
cp -r arbor-zoo/algotune_knn /tmp/algotune_knn
cd /tmp/algotune_knn
git init -q && git add -A && git commit -qm baseline
arbor   # Arbor 读 README、确认任务,然后开始迭代
```

## 新增一个基准

1. 起架子:`arbor benchmark scaffold arbor-zoo/<name> --style zoo`。它写一个 eval 占位、
   `solution.py` 占位、自然语言 `README.md` 和 `PROVENANCE.md`——但绝不替你写解法。
2. 填好基线(`solution.py`)、eval(`eval.py`/`eval.sh`)、README(给 Arbor 看)、PROVENANCE(给人看)。
3. 反复 `arbor benchmark verify arbor-zoo/<name>` 直到退出 0,再由维护者接受。起草可以自动,
   **接受是人工这一步**。

端到端的例子见
[`arbor-zoo/algotune_knn`](https://github.com/RUC-NLPIR/Arbor/tree/main/arbor-zoo/algotune_knn)。
