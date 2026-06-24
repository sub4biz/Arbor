# Benchmark Zoo — overview & roadmap

This page is the **big picture** of the benchmark zoo: what it is, how we think about it,
what's built versus planned, and how you use it today. For the exact folder format and the
verifier's checks, see the [format reference](zoo.md).

## What it is

The **benchmark zoo** is a curated, verifiable set of optimization problems that Arbor can
be pointed at — packaged in one standard format so anyone can re-run them and check the
numbers. It lives in [`arbor-zoo/`](https://github.com/RUC-NLPIR/Arbor/tree/main/arbor-zoo),
one folder per benchmark.

Two principles shape everything:

- **Regression harness first, showcase second.** The zoo's first job is to keep Arbor
  honestly tested on a small set of hand-checked, reproducible tasks. Being an outward
  showcase is secondary.
- **Quality-capped, not a trophy board.** It is deliberately **not** a leaderboard of our
  own results. We use representative work to *position a reusable, fairly-baselined task* —
  never to catalogue how many papers we beat.

## The one idea to internalize

**A pack is not "a dataset" — it is a locked optimization problem:**

> `data + frozen substrate + edit surface + metric + reference baseline`

The same dataset climbed from a different angle (tune the prompt vs. fine-tune the model vs.
design a scaffold) is a **different pack**. The *angle is the pack*, encoded in the README
front-matter (what's editable, what's frozen, what's measured). This is why "how you climb a
benchmark" is decided when the pack is authored, not at run time.

## How we categorize (the mental map)

**Two layers.**

| Layer | What | Purpose |
| --- | --- | --- |
| **Stable core** | synthetic / self-contained tasks (e.g. `algotune_knn`) | Arbor's regression harness — stable, cheap, deterministic |
| **Frontier shelf** | tasks anchored on representative *hot work* | track the field; the "climb real benchmarks" use case |

**The freeze axis** — every pack declares what it holds fixed, which decides what it measures:

- **Freeze the model** (edit a scaffold/prompt) → measures the *method*; cheap, clean
  attribution, narrow coverage.
- **Freeze a budget** (compute/wall-clock; edit training + scaffold + data) → *any* mechanism
  competes on equal footing (the MLE-bench style); broad coverage, needs the compute.

**Task shapes that fit** — anything where you optimize an *artifact* against a held-out score:
algorithm/efficiency (kernels, AlgoTune), ML-engineering/tabular (Kaggle/MLE-bench),
coding/agents (SWE-bench), prompt/reasoning scaffolds, and training-efficiency. **Out of
scope**: tasks that only *evaluate a frozen model* (raw multimodal QA) or need hardware/sim
(embodied robotics) — there is no artifact for Arbor to optimize.

## What's built vs. planned

| Capability | Command / artifact | Status |
| --- | --- | --- |
| Pack format + front-matter contract (incl. `frozen:`) | `arbor-zoo/<name>/` | ✅ shipped |
| The gate that admits a pack | `arbor benchmark verify` | ✅ shipped |
| Index the packs | `arbor benchmark list` | ✅ shipped |
| Make a local dir Arbor-ready / author a pack | `arbor benchmark scaffold` (+ MCP tool, intake wiring) | ✅ shipped |
| Acquire a remote benchmark + scaffold a draft | `arbor benchmark add` (git / HF, global cache) | ✅ spine shipped |
| First verified dogfood pack | `arbor-zoo/algotune_knn` | ✅ shipped |
| **Collection intelligence** — survey a direction/work → harvest baseline → bring it up | the agent stages behind `add` | ⏳ planned |
| More curated packs across task shapes | `arbor-zoo/…` | ⏳ ongoing |
| Browsable zoo / leaderboard view | — | ⏳ deferred |
| Optimizing across many benchmarks at once | — | 🔭 far-future |

The internal design behind the collection feature lives in the dev notes
(`docs/dev/benchmark-add.md`) along with a researched
[backlog of collectable benchmarks](https://github.com/RUC-NLPIR/Arbor/blob/main/docs/dev/benchmark-backlog.md).

## How you use it today

There are four entry points, from "just run it" to "add a new one":

1. **Run Arbor on an existing pack.** Copy a pack out of the checkout (Arbor uses git
   worktrees), then point Arbor at it:
   ```bash
   cp -r arbor-zoo/algotune_knn /tmp/algotune_knn
   cd /tmp/algotune_knn && git init -q && git add -A && git commit -qm baseline
   arbor   # confirm the contract, then it iterates
   ```
2. **Make your own task Arbor-ready.** If you have code but no runnable eval / split, scaffold
   the measurement plumbing (it never writes the solution):
   ```bash
   arbor benchmark scaffold ./my_task --style light    # eval + split + solution stub
   arbor benchmark scaffold ./my_task --style zoo       # + README contract + PROVENANCE
   ```
3. **Author a zoo pack.** Scaffold with `--style zoo`, fill in the baseline + eval +
   PROVENANCE, then gate it: `arbor benchmark verify arbor-zoo/<name>` until it exits 0, and a
   maintainer accepts it. Drafting may be automated; **acceptance is a human step**.
4. **Collect a benchmark** (Phase 1 today). Acquire a remote benchmark into the global cache
   and scaffold a draft to complete:
   ```bash
   arbor benchmark add https://github.com/owner/repo --name my_bench
   ```

## The discipline (why a green check means something)

A pack only counts when these hold — partly machine-enforced by `verify`, partly human-reviewed:

- **Held-out**: dev/test are provably disjoint; merges gate on the protected test split.
- **Frozen substrate**: what's fixed is declared, so an improvement is attributable and two
  runs are comparable (no winning by swapping in a bigger model).
- **Provenance + human acceptance**: source, baseline, and a mandatory contamination
  assessment are written down and read by a maintainer — never auto-accepted.

That's the whole shape: the zoo marks out *locked optimization problems*, Arbor runs its
normal loop inside them, and the verifier + provenance keep the results trustworthy.

See the [format reference](zoo.md) to author one, or the
[roadmap](roadmap.md) for where the wider effort is going.
