# SpecForge

SpecForge is a **Python-first grounding + governance layer** for **spec-driven development** in brownfield repositories.

It’s built for workflows where the hard part isn’t “get tests green,” but:

* staying **repo-aware** across long iterations without drowning in context,
* preventing **duplicate functionality** and scope creep,
* producing a clear **spec + plan + UX acceptance criteria** before code is written,
* guiding **out-of-code steps** (GTM, GrowthBook, dashboards, admin panels),
* validating changes against the **intended experience** (not just compilation).

SpecForge integrates:

* **Snapshotter (LangGraph)** for deterministic repo grounding artifacts
* **OpenSpec** as the **planning system** (Specs vs Changes artifacts + `/opsx:*` lifecycle)
* **External executors** (Codex CLI / Claude Code / Aider / Cursor / etc.) for code edits

> **Default stance:** **OpenSpec is the planning system. SpecForge adds grounding + guardrails + reports.**
> SpecForge does **not** own the OpenSpec lifecycle, and does **not** run `openspec` CLI by default.

---

## Core idea

SpecForge ties together three things:

1. **Grounding (Snapshot artifacts)**
   A bounded, auditable view of the repo: architecture summary, dependency graph, evidence packs, risks, and fingerprints.

2. **Intent ledger (OpenSpec artifacts)**
   The durable, in-repo record of:

    * current behavior (`openspec/specs/`)
    * proposed changes (`openspec/changes/<id>/`)

3. **Governance + validation (SpecForge)**
   Rules and reports that enforce:

    * scope fences (“only these paths may change”)
    * no-duplication requirements (new modules require evidence)
    * fail-loud contracts (no silent back-compat)
    * human runbooks for UX/out-of-code steps

---

## Workflow (default: OpenSpec-owned planning)

### Cycle overview

1. **Snapshot the repo (manual trigger)**

* Run Snapshotter to produce a new snapshot directory with deterministic artifacts.

2. **Create/continue an OpenSpec change (you run OpenSpec)**

* OpenSpec lives in the target repo and stores:

    * `openspec/specs/` (current truth)
    * `openspec/changes/<id>/` (proposal + delta specs + design + tasks)

3. **Inject grounding into the OpenSpec change (SpecForge)**

* SpecForge reads snapshot artifacts and writes a **Grounding Digest** into the change (e.g. `context.md`):

    * key modules / entry points
    * dependency hotspots
    * “do not duplicate” warnings
    * risks/gaps pulled from snapshot analysis
    * snapshot + commit fingerprint for auditability

4. **Plan in OpenSpec artifacts (OpenSpec + you)**

* You and the “architect brain” refine:

    * `proposal.md` (WHY)
    * `specs/**/*.md` (WHAT: delta specs ADDED/MODIFIED/REMOVED + scenarios)
    * `design.md` (HOW, optional)
    * `tasks.md` (DO: implementation checklist)

5. **Execute using an external tool (you)**

* Use OpenSpec’s tool skills (`/opsx:apply`) or your preferred executor.
* SpecForge can generate executor-ready payloads (scoped prompts), but does not own the edit/run loop.

6. **Validate + report (SpecForge)**

* Governance checks:

    * scope fence (only allowed paths touched)
    * no new modules without evidence + justification
    * contract/invariant checks (“fail loud” rules)
* Human runbook output:

    * UX/flow verification checklist
    * GrowthBook / GTM steps & expected outcomes
* Reporting:

    * “what changed”
    * “what to manually verify”
    * “what to do next”

7. Repeat with the next chunk until done.

> Optional later: SpecForge can add an **OpenSpec CLI bridge** for `status/validate` if the workflow benefits from it. Not in v0 default.

---

## Where LangGraph fits (and where it doesn’t)

Snapshotter already runs on **LangGraph**. SpecForge follows a simple rule:

### Use LangGraph where stateful orchestration is valuable

SpecForge uses LangGraph only for workflows that benefit from:

* branching (“explore” vs “build”)
* checkpoints and iteration
* stop-early on FAIL
* structured multi-step reasoning

Typical LangGraph flows (optional):

* **Architect flow**: produce/refine OpenSpec artifacts and governed work chunks
* **Validation flow**: run governance checks + generate reports
* **Explore flow**: repo-grounded investigation and question generation

### Don’t use LangGraph for deterministic plumbing

These remain simple, synchronous Python modules:

* reading snapshot artifacts
* building `context.md` grounding digests
* parsing `tasks.md` into chunks
* git diff and changed-file reporting
* scope fence enforcement

This keeps SpecForge testable, predictable, and lightweight.

---

## Installation (uv-managed)

SpecForge is designed to be run from a **uv-managed virtual environment**.

### Prerequisites

* Python 3.11+
* `uv` installed
* Snapshot artifacts produced by Snapshotter (or a compatible snapshot pipeline)
* OpenSpec installed/used inside target repos (SpecForge reads/writes artifacts only by default)

### Setup

```bash
git clone <this-repo>
cd specforge

uv venv
uv sync
```

### Run

```bash
uv run specforge --help
```

### Development commands

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

---

## Quickstart (default mode)

> In this mode, you run OpenSpec commands yourself. SpecForge only reads/writes OpenSpec files.

1. Run Snapshotter (manual)

```bash
uv run snapshotter --dotenv --dry-run
# produces: ./snapshots/<repo>/<timestamp>/
```

2. Create or continue an OpenSpec change (inside the target repo)

```bash
openspec init
/opsx:new add-event-tracking
/opsx:ff
# refine proposal/specs/design/tasks as needed
```

3. Start a SpecForge cycle and inject grounding

```bash
uv run specforge cycle start \
  --repo /path/to/target-repo \
  --snapshot /path/to/snapshots/<repo>/<timestamp> \
  --change add-event-tracking

uv run specforge inject grounding --change add-event-tracking
```

4. Execute using your preferred tool

* Apply tasks using `/opsx:apply` in your assistant, **or**
* Use your preferred executor to implement the tasks

5. Validate + report (governance + runbook)

```bash
uv run specforge validate --change add-event-tracking --strict
uv run specforge report --change add-event-tracking
```

---

## What SpecForge writes and stores

### Inside the target repo (OpenSpec change folder)

* `openspec/changes/<id>/context.md` — Grounding Digest (generated by SpecForge)
* `openspec/changes/<id>/runbook.md` — optional human verification steps (generated)
* `openspec/changes/<id>/governance.yml` — optional scope fence + rule config
* `openspec/changes/<id>/validation.md` — optional results + “what to verify next”

### Inside SpecForge local storage

* `storage/cycles/<cycle-id>.json` — snapshot fingerprint + change linkage
* `storage/reports/<cycle-id>.md` — human-friendly cycle report

---

## Key components

### Snapshot grounding (external input)

SpecForge expects snapshot artifacts (paths configurable), typically including:

* `ARCHITECTURE_SUMMARY_SNAPSHOT.json`
* `repo_index.json`
* `DEPENDENCY_GRAPH.json`
* `GAPS_AND_INCONSISTENCIES.json`
* `artifact_manifest.json`

SpecForge uses these to:

* onboard each cycle quickly,
* prevent duplication and hallucinated structures,
* tie every plan and validation report to concrete evidence and fingerprints.

### OpenSpec integration (file-based by default)

OpenSpec provides:

* Specs (`openspec/specs/`) describing the **current** behavior
* Changes (`openspec/changes/<id>/`) describing **proposed** modifications

SpecForge reads/writes:

* `context.md` (grounding digest)
* optional `runbook.md`, `governance.yml`, `validation.md`

SpecForge does **not** call OpenSpec CLI by default.

### Governance validator (fail-loud)

SpecForge enforces:

* **Scope fences:** only approved paths may change
* **No duplication:** new modules require evidence pointers + justification
* **Contract rules:** explicit invariants (e.g., “no back-compat glue”)
* **Audit trail:** snapshot fingerprint + OpenSpec change id + diff summary

### External executors (optional adapters)

SpecForge can optionally provide thin adapters for:

* Codex CLI
* Claude Code
* Aider
* Manual prompt output mode

Adapters are intentionally thin: they accept a governed chunk and produce a patch/diff or instructions.

---

## Proposed repository structure (Python-first)

```
specforge/
├── pyproject.toml
├── README.md
├── src/
│   └── specforge/
│       ├── __init__.py
│       ├── cli/
│       │   ├── main.py
│       │   ├── cycle_cmd.py
│       │   ├── inject_cmd.py
│       │   ├── plan_cmd.py
│       │   ├── validate_cmd.py
│       │   └── report_cmd.py
│       ├── core/                       # deterministic, sync modules
│       │   ├── cycle_manager.py
│       │   ├── state_store.py
│       │   ├── grounding/
│       │   │   ├── snapshot_reader.py
│       │   │   ├── digest_builder.py
│       │   │   └── evidence.py
│       │   ├── openspec/
│       │   │   ├── connector.py        # file-based connector
│       │   │   └── tasks_parser.py
│       │   ├── governance/
│       │   │   ├── rules.py
│       │   │   ├── change_tracker.py
│       │   │   └── validator.py
│       │   └── runbooks/
│       │       ├── model.py
│       │       └── renderers.py
│       ├── flows/                      # LangGraph orchestration (optional)
│       │   ├── architect_flow.py
│       │   ├── validate_flow.py
│       │   └── explore_flow.py
│       ├── llm/
│       │   ├── client.py
│       │   ├── prompts/
│       │   └── architect.py
│       └── types/
│           ├── chunks.py
│           ├── snapshot.py
│           └── validation.py
├── tests/
│   ├── test_tasks_parser.py
│   ├── test_scope_fence.py
│   ├── test_digest_builder.py
│   └── test_validate_flow.py
└── docs/
    ├── workflow.md
    ├── governance_rules.md
    └── snapshot_contract.md
```

---

## Roadmap

**v0 (file-based, minimal dependencies)**

* read snapshot artifacts + build Grounding Digest
* read/write OpenSpec change files (`context.md`, `runbook.md`)
* parse `tasks.md` into governed chunks
* scope fence validator using git diff
* markdown report output

**v1 (optional conveniences)**

* optional OpenSpec CLI bridge for `status/validate` (if it proves useful)
* OpenSpec schema fork with baked-in governance sections
* “no duplication” checks using repo_index + dependency graph
* interactive status view (cycle progress, next chunk)

---
