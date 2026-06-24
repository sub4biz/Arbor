# 基准动物园 —— 总览与路线

这一页是基准动物园的**全景**:它是什么、我们怎么想、做了什么、还没做什么、现在怎么用。确切的
文件夹格式和校验器检查见[格式参考](zoo.md)。

## 它是什么

**基准动物园**是一组经过筛选、可校验的优化题,可以让 Arbor 对准它们——用同一套标准格式打包,
让任何人都能复跑并核对数字。它放在
[`arbor-zoo/`](https://github.com/RUC-NLPIR/Arbor/tree/main/arbor-zoo) 里,每个基准一个文件夹。

两条原则贯穿始终:

- **回归 harness 优先,展示其次。** zoo 的首要职责是用一小批人工核对、可复跑的任务,让 Arbor
  始终被诚实地测着。对外展示是次要的。
- **质量封顶,不做战绩榜。** 它**刻意不做**我们自己结果的排行榜。我们用代表性工作来*把一道
  可复用、baseline 公平的任务定位准*——而不是去攒"我们超过了多少篇论文"。

## 要内化的那一个核心观念

**一个 pack 不是"一个数据集",而是一道锁死的优化题:**

> `数据 + 冻结底座 + 编辑面 + 指标 + 参照基线`

同一个数据集,从不同角度刷(调 prompt vs 微调模型 vs 设计 scaffold),就是**不同的 pack**。
*角度即 pack*,编码在 README front-matter 里(什么可改、什么冻结、测什么)。所以"怎么刷一个
benchmark"是在**写 pack 那一刻**决定的,不在运行时。

## 我们的分类思路(心智地图)

**两层结构。**

| 层 | 是什么 | 用途 |
| --- | --- | --- |
| **稳定核心层** | 合成/自包含任务(如 `algotune_knn`) | Arbor 的回归 harness——稳定、便宜、确定性 |
| **前沿货架层** | 锚定代表性*热门工作*的任务 | 追踪前沿;"刷真实 benchmark"的场景 |

**冻结轴** —— 每个 pack 声明它固定什么,这决定了它测的是什么:

- **冻模型**(改 scaffold/prompt)→ 测*方法*;便宜、归因干净、覆盖窄。
- **冻预算**(算力/wall-clock;改训练+scaffold+数据)→ *任意*机制平等竞争(MLE-bench 式);
  覆盖广,但要算力撑得住。

**适合的任务形态** —— 凡是"优化一个 artifact、对着 held-out 分数刷"的都适合:算法/效率(kernel、
AlgoTune)、ML 工程/表格(Kaggle/MLE-bench)、代码/agent(SWE-bench)、prompt/推理 scaffold、
训练效率。**不在范围内**:只*评测一个冻结模型*的(纯多模态 QA)、或要硬件/仿真的(具身机器人)
——那里没有可供 Arbor 优化的 artifact。

## 做了什么 vs 还没做

| 能力 | 命令 / 产物 | 状态 |
| --- | --- | --- |
| pack 格式 + front-matter 契约(含 `frozen:`) | `arbor-zoo/<name>/` | ✅ 已交付 |
| 准入门 | `arbor benchmark verify` | ✅ 已交付 |
| 索引 pack | `arbor benchmark list` | ✅ 已交付 |
| 把本地目录补成 Arbor-ready / 写一个 pack | `arbor benchmark scaffold`(+ MCP 工具、intake 接线) | ✅ 已交付 |
| 获取远端 benchmark + 起草草稿 | `arbor benchmark add`(git / HF,全局缓存) | ✅ 骨架已交付 |
| 第一个过校验的 dogfood pack | `arbor-zoo/algotune_knn` | ✅ 已交付 |
| **收集智能** —— 综述一个方向/工作 → 收割 baseline → 跑通 | `add` 背后的 agent 阶段 | ⏳ 计划中 |
| 跨形态的更多策展 pack | `arbor-zoo/…` | ⏳ 进行中 |
| 可浏览的 zoo / leaderboard 视图 | — | ⏳ 暂缓 |
| 同时对多个 benchmark 优化 | — | 🔭 远期 |

收集功能背后的内部设计在 dev 笔记(`docs/dev/benchmark-add.md`)里,并附了一份调研过的
[可收集 benchmark 待办清单](https://github.com/RUC-NLPIR/Arbor/blob/main/docs/dev/benchmark-backlog.md)。

## 现在怎么用

四个入口,从"直接跑"到"加一个新的":

1. **在现有 pack 上跑 Arbor。** 把 pack 拷出检出目录(Arbor 用 git worktree),再让 Arbor 对准它:
   ```bash
   cp -r arbor-zoo/algotune_knn /tmp/algotune_knn
   cd /tmp/algotune_knn && git init -q && git add -A && git commit -qm baseline
   arbor   # 确认契约,然后它开始迭代
   ```
2. **把你自己的任务补成 Arbor-ready。** 如果你有代码但没有能跑的 eval / 划分,补上测量管线
   (它绝不写解法):
   ```bash
   arbor benchmark scaffold ./my_task --style light    # eval + 划分 + solution 占位
   arbor benchmark scaffold ./my_task --style zoo       # + README 契约 + PROVENANCE
   ```
3. **写一个 zoo pack。** 用 `--style zoo` 脚手架,填好 baseline + eval + PROVENANCE,然后过门:
   反复 `arbor benchmark verify arbor-zoo/<name>` 直到退出 0,再由维护者接受。起草可自动,
   **接受是人工步骤**。
4. **收集一个 benchmark**(目前是 Phase 1)。把远端 benchmark 拉进全局缓存并起草草稿待补全:
   ```bash
   arbor benchmark add https://github.com/owner/repo --name my_bench
   ```

## 纪律(为什么一个绿勾是有分量的)

一个 pack 只有满足这些才算数——一部分由 `verify` 机器强制,一部分人工审核:

- **留出**:dev/test 可证明不相交;merge 以受保护的 test 划分为门。
- **冻结底座**:固定了什么是声明出来的,所以"提升"可归因、两次 run 可比(不能靠换更大模型取胜)。
- **来源 + 人工接受**:来源、baseline、以及一份必填的污染评估,都写下来并由维护者读过——绝不
  自动接受。

整体就是这个形状:zoo 划出一道道*锁死的优化题*,Arbor 在里面跑它本来的循环,校验器 + 来源卡片
保证结果可信。

写一个 pack 见[格式参考](zoo.md),整条线的去向见[路线图](roadmap.md)。
