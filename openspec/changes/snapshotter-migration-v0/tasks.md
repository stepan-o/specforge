## 1. Prepare workspace package shell

- [ ] 1.1 Create package directory `packages/specforge_snapshotter/` with `src/` layout
- [ ] 1.2 Add `packages/specforge_snapshotter/pyproject.toml` with correct name/version and `requires-python (>=3.11,<3.13)`
- [ ] 1.3 Add workspace wiring so uv recognizes the package (confirm it’s listed in root `[tool.uv.workspace].members`)
- [ ] 1.4 Decide and document the console script name for Snapshotter (e.g., `snapshotter`) and add it to the package scripts

## 2. Migrate Snapshotter code (no behavior changes)

- [ ] 2.1 Copy Snapshotter source files into `packages/specforge_snapshotter/src/snapshotter/` preserving module layout
- [ ] 2.2 Ensure imports resolve correctly in the new package context (no relative path breakage)
- [ ] 2.3 Preserve CLI contract: verify code still reads payload ONLY from `SNAPSHOTTER_JOB_JSON`
- [ ] 2.4 Preserve output/workdir contracts: confirm code still writes to `out/<repo_slug>/<timestamp_utc>/<job_id>` and uses `.snapshotter_tmp`
- [ ] 2.5 Preserve Pass2 fail-fast: confirm missing `OPENAI_API_KEY` still hard-errors before any API call
- [ ] 2.6 Preserve S3 behavior: confirm upload code path still uses boto3 defaults, region rules, and SSE `AES256`

## 3. Dependency + lockfile integration

- [ ] 3.1 Add Snapshotter runtime deps to `packages/specforge_snapshotter/pyproject.toml` (LangGraph + required libs, boto3, etc.)
- [ ] 3.2 Run `uv sync --all-packages` and confirm lockfile resolves cleanly
- [ ] 3.3 Run `uv run python -c "import snapshotter; print(snapshotter.__file__)"` (or the correct import) to confirm package import works

## 4. CLI wiring smoke checks (repo root)

- [ ] 4.1 Run `uv run snapshotter --help` (or the chosen console script) and confirm CLI is reachable from repo root
- [ ] 4.2 Verify optional dotenv loading still works as convenience only (`--dotenv` / `--dotenv-override`)

## 5. End-to-end smoke test (local run)

- [ ] 5.1 Create a minimal valid `SNAPSHOTTER_JOB_JSON` payload for a small test repo/ref (local-only config is fine)
- [ ] 5.2 Export required env vars (`SNAPSHOTTER_JOB_JSON`, `OPENAI_API_KEY`) and run Snapshotter from repo root
- [ ] 5.3 Confirm artifacts are produced under `out/<repo_slug>/<timestamp_utc>/<job_id>`
- [ ] 5.4 Confirm failure modes:
    - Missing `SNAPSHOTTER_JOB_JSON` fails fast
    - Missing `OPENAI_API_KEY` fails fast at Pass2

## 6. Docs + cleanup

- [ ] 6.1 Add README notes (or repo docs) describing Snapshotter usage in this monorepo: required env vars, payload schema keys, default output layout
- [ ] 6.2 Ensure `out/` and `.snapshotter_tmp/` remain gitignored (already set) and no generated artifacts are committed
- [ ] 6.3 Run `openspec validate snapshotter-migration-v0` to confirm all artifacts remain valid
