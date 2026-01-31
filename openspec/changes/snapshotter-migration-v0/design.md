## Context

Snapshotter currently exists as an independent Python package that runs a LangGraph pipeline to generate repo artifacts. SpecForge is a Python-first uv workspace monorepo that will treat OpenSpec as the planning system and add grounding/guardrails/reporting on top of Snapshotter outputs.

Constraints (must be preserved):
- Configuration contract: Snapshotter job payload is provided ONLY via `SNAPSHOTTER_JOB_JSON` (env var JSON object string). No file/stdin payload paths are introduced.
- Pass2 semantic requires `OPENAI_API_KEY` and fails hard if missing.
- Default output layout: `out/<repo_slug>/<timestamp_utc>/<job_id>`.
- Workdir remains `.snapshotter_tmp`.
- Optional S3 upload behavior remains unchanged (boto3 resolution + region rules + SSE AES256).

Stakeholders:
- Developer running snapshot cycles locally (CLI + artifacts).
- SpecForge “architect/validator” flows that consume Snapshotter artifacts for grounding and reporting.
- OpenSpec change workflows that need stable, auditable artifacts per cycle.

## Goals / Non-Goals

**Goals:**
- Migrate Snapshotter into this monorepo as a uv workspace member (`packages/specforge_snapshotter`) with behavior unchanged.
- Preserve CLI entrypoint and runtime configuration contract (payload-only env var + fail-fast validations).
- Keep Snapshotter artifact outputs identical, including default output directory layout and workdir usage.
- Provide a minimal smoke-test workflow to verify Snapshotter runs end-to-end from this repo.

**Non-Goals:**
- No functional changes to Snapshotter pipeline, artifacts, schemas, or LangGraph graph structure.
- No “auto-iterate until green” execution loop (tests and retries remain developer-driven).
- No refactors, performance work, or redesign of configuration/loading beyond what is required for packaging.
- No new SpecForge integrations in this change (consumption of artifacts is handled in later changes).

## Decisions

- **Decision: Keep Snapshotter as an isolated workspace package**
    - Rationale: Minimizes coupling and preserves behavior. Allows SpecForge to depend on it without inlining code into the core package.
    - Alternative: Copy Snapshotter modules directly under SpecForge core. Rejected because it increases coupling and raises the risk of accidental behavior changes.

- **Decision: Preserve CLI contract exactly (SNAPSHOTTER_JOB_JSON payload-only)**
    - Rationale: This is a locked contract and is already relied upon in existing workflows (payload-only, reproducible, no “helpful” fallbacks).
    - Alternative: Add file-based job payload input. Rejected because it violates the contract and increases ambiguity in execution.

- **Decision: Preserve default output/workdir conventions**
    - Rationale: Downstream tooling expects artifacts in stable locations and Snapshotter already has deterministic path logic.
    - Alternative: Relocate outputs under `snapshots/` or `storage/`. Rejected for this change to avoid breaking paths and to keep migration risk low. Output relocation can be considered later behind a versioned contract if needed.

- **Decision: Workspace wiring via uv + console script**
    - Rationale: Enables `uv run snapshotter ...` (or equivalent) from repo root without external installation and matches the repo’s Python-first approach.
    - Alternative: Invoke Snapshotter only via `python -m ...`. Rejected as primary UX; acceptable as a fallback, but console script is the intended entrypoint.

## Risks / Trade-offs

- [Risk] Dependency resolution changes under the monorepo workspace could alter runtime behavior (version drift).
  → Mitigation: Pin/lock dependencies via uv lockfile and run a smoke test that exercises Pass1 + Pass2 against a known repo.

- [Risk] CLI entrypoint changes accidentally break the env contract or argument surface.
  → Mitigation: Treat CLI as part of the spec; add a minimal “contract smoke test” checklist and keep the CLI module structure unchanged as much as possible.

- [Risk] Output path assumptions break when run from repo root.
  → Mitigation: Verify `out/<repo_slug>/<timestamp_utc>/<job_id>` is created and populated; ensure relative paths are resolved the same way as before.

- [Trade-off] This change intentionally avoids improvements (e.g., nicer UX, output location customization).
  → Mitigation: Defer enhancements to later OpenSpec changes after migration is stable.

## Migration Plan

1. Import Snapshotter code into `packages/specforge_snapshotter` preserving module layout and public entrypoints.
2. Add/confirm workspace package metadata (pyproject, console scripts) so Snapshotter is runnable from repo root using uv.
3. Ensure required env vars and configuration contract remain unchanged (`SNAPSHOTTER_JOB_JSON`, `OPENAI_API_KEY`).
4. Run a local smoke test:
    - Execute a run against a small repo/ref with a minimal but valid job payload.
    - Confirm outputs are written under `out/<repo_slug>/<timestamp_utc>/<job_id>`.
5. If issues occur, rollback by reverting the package import and workspace wiring changes (no data migrations involved).

## Open Questions

- What is the exact console script name we want exposed from the workspace (`snapshotter` vs `specforge-snapshotter`), and do we need to preserve an existing name for backwards compatibility?
- Do we want to keep S3 upload enabled by default, or recommend “local-only” runs unless explicitly configured?
