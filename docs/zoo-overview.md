# Benchmark Zoo

Arbor works by pointing at a task that prints a score, then repeatedly editing the code,
running the eval, and keeping the changes that improve the score. The **benchmark zoo** is a
collection of such tasks — each packaged in one standard format, so you can grab one and let
Arbor start optimizing it right away. It lives in
[`arbor-zoo/`](https://github.com/RUC-NLPIR/Arbor/tree/main/arbor-zoo), one folder per benchmark.

## What it's for

- **Ready-made tasks to optimize.** Each benchmark ships an eval and a baseline — point
  `arbor` at it and it starts improving the score.
- **Turn your own task into one.** Have code but no runnable eval yet? One command adds the
  eval scaffolding so Arbor can run it.
- **Collect new ones (in progress).** Have Arbor fetch a benchmark from GitHub / HuggingFace
  and shape it into the zoo format.

## What a benchmark looks like

One folder with three things:

- a **README** — what the task is and which score to optimize;
- **baseline code** — Arbor's starting point, and the only part it's allowed to edit;
- an **eval script** — run it and it prints one `score:` line; it's protected, so Arbor can't
  game it.

Arbor's loop is just: edit the baseline → run the eval → keep the change if the score went up,
and repeat.

## Entry points

| What you want to do | Command |
| --- | --- |
| See what's in the zoo | `arbor benchmark list` |
| Optimize a benchmark with Arbor | copy it out, `git init`, then run `arbor` in it |
| Check a benchmark is valid | `arbor benchmark verify <dir>` |
| Make your own code Arbor-ready | `arbor benchmark scaffold <dir>` |
| Pull a benchmark from GitHub / HF | `arbor benchmark add <url> --name <name>` |

Running one, start to finish:

```bash
cp -r arbor-zoo/algotune_knn /tmp/algotune_knn   # copy out of the Arbor checkout
cd /tmp/algotune_knn && git init -q && git add -A && git commit -qm baseline
arbor                                             # confirm the task, then it iterates
```

## What's here, what's next

- ✅ **Available now:** the format, `verify`, `list`, `scaffold`, the `add` spine, and the
  first example benchmark, `algotune_knn`.
- ⏳ **In progress:** making `add` smarter (research the benchmark and bring its baseline up
  automatically), and adding more benchmarks.

To author one, see the [format reference](zoo.md). For where this is heading, see the
[roadmap](roadmap.md).
