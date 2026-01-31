## Why

We need Snapshotter available inside the SpecForge monorepo so our OpenSpec planning cycles can be reliably grounded in deterministic repo artifacts, and so SpecForge can add guardrails/reporting on top of those outputs. We’re doing this now to reduce onboarding overhead and prevent duplicated functionality during iterative development cycles.

## What Changes

- Add Snapshotter as a first-class workspace package in this repo (uv workspace member).
- Preserve Snapshotter behavior and outputs (artifact contracts) exactly as-is (no functional changes).
- Preserve the CLI contract: Snapshotter execution is configured via `SNAPSHOTTER_JOB_JSON` only (payload-only, env var string; no stdin/file payload input).
- Ensure Python version + dependency boundaries remain compatible with the SpecForge workspace (`>=3.11,<3.13`, dev pinned to `3.12`).
- Add a minimal smoke-test path to prove Snapshotter runs end-to-end from this monorepo under the same configuration contract.
- **Non-goals:** No new features, no refactors, no LangGraph changes, no artifact format changes, no “auto-iterate until green” execution loop.

## Capabilities

### New Capabilities
- `repo-snapshotting`: Run Snapshotter locally to generate deterministic repo artifacts (index + packs + summaries) that downstream tools can consume.

### Modified Capabilities
- (none)

## Impact

- **CLI / Config contract (must remain unchanged):**
    - Snapshotter requires `SNAPSHOTTER_JOB_JSON` env var containing a JSON object string (payload-only).
    - Optional `--dotenv` / `--dotenv-override` may load env vars for convenience, but the payload still must be supplied via `SNAPSHOTTER_JOB_JSON`.
    - Job schema is validated at runtime against `snapshotter/job.py` (pydantic `Job`).

- **Required secrets:**
    - Pass2 semantic analysis requires `OPENAI_API_KEY` in the environment and fails hard if missing.
    - S3 upload is optional, but when enabled:
        - job payload must include `output.s3_bucket` and `output.s3_prefix`
        - boto3 credentials must resolve at runtime (standard AWS mechanisms)
        - region can be provided via `--aws-region` or `AWS_REGION` / `AWS_DEFAULT_REGION`
        - uploads expect SSE `AES256` (bucket policy requirement)

- **Default output layout (must remain unchanged):**
    - Snapshotter writes to: `out/<repo_slug>/<timestamp_utc>/<job_id>`
    - Uses `.snapshotter_tmp` as workdir for cloning/inspection.

- **Codebase:**
    - Introduces a `specforge_snapshotter` workspace member (plus any shared utilities it depends on).
    - Locks Snapshotter deps under workspace resolution (LangGraph + related libs, boto3, etc.).

- **Downstream integration:**
    - Unblocks SpecForge “grounding” steps that read Snapshotter outputs and inject context into OpenSpec change cycles.
