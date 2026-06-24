# 基准库（Benchmark Zoo）

Arbor 的工作方式很简单:对着一个能打分的任务,反复改代码、跑评测、把让分数变好的改动留下来。
**基准库**就是一批这样的任务的集合——每个都打包成统一格式,拿来就能直接让 Arbor 上手优化。它放在
仓库的 [`arbor-zoo/`](https://github.com/RUC-NLPIR/Arbor/tree/main/arbor-zoo) 下,一个文件夹一个基准。

## 它用来干什么

- **现成的任务,直接刷。** 库里每个基准都自带评测和一份基线,`arbor` 对准它就能开始优化、刷分。
- **把你自己的任务也变成这样。** 有代码、但还不能评测?一条命令补上评测的架子,Arbor 就能跑了。
- **自动收集(开发中)。** 让 Arbor 自己去 GitHub / HuggingFace 上把一个 benchmark 拉下来,整理成
  库里的格式。

## 一个基准长什么样

就是一个文件夹,里面三样东西:

- 一份 **README**:这个任务是什么、要优化哪个分数;
- 一份 **基线代码**:Arbor 的优化起点,也是它唯一能改的部分;
- 一个 **评测脚本**:跑一下打印一行 `score:`;它受保护,Arbor 改不了它、也就没法作弊。

Arbor 做的事就是一个循环:改基线 → 跑评测 → 分数涨了就留下,如此反复。

## 几个入口

| 你想做什么 | 命令 |
| --- | --- |
| 看库里有哪些基准 | `arbor benchmark list` |
| 在某个基准上跑 Arbor 优化 | 把它拷出仓库,`git init`,在目录里跑 `arbor` |
| 检查一个基准合不合格 | `arbor benchmark verify <目录>` |
| 把你自己的代码补成 Arbor 能跑的 | `arbor benchmark scaffold <目录>` |
| 从 GitHub / HF 拉一个 benchmark 进来 | `arbor benchmark add <地址> --name <名字>` |

完整跑一个的例子:

```bash
cp -r arbor-zoo/algotune_knn /tmp/algotune_knn   # 拷出 Arbor 仓库
cd /tmp/algotune_knn && git init -q && git add -A && git commit -qm baseline
arbor                                             # 确认任务,然后它开始迭代
```

## 现在有什么、还在做什么

- ✅ **已经能用:** 基准格式、校验(`verify`)、列表(`list`)、补脚手架(`scaffold`)、收集的主体
  (`add`),以及第一个示例基准 `algotune_knn`。
- ⏳ **还在做:** 让 `add` 更聪明(自动调研 benchmark、把基线跑通),以及加入更多基准。

想自己写一个基准,详细格式见[格式参考](zoo.md);整条线的规划见[路线图](roadmap.md)。
