## ADDED Requirements

### Requirement: Snapshotter is available as a workspace package
Snapshotter MUST be included as a first-class uv workspace member in the SpecForge monorepo and remain runnable from the repo root.

#### Scenario: Workspace invocation works
- **WHEN** a developer runs Snapshotter from the SpecForge repo root (via the workspace entrypoint)
- **THEN** Snapshotter starts successfully without requiring installation from an external repo

### Requirement: Payload-only configuration via SNAPSHOTTER_JOB_JSON is preserved
Snapshotter MUST accept its job payload ONLY via the `SNAPSHOTTER_JOB_JSON` environment variable as a JSON object string. Snapshotter MUST NOT introduce file-based or stdin-based payload inputs.

#### Scenario: Valid payload in env is accepted
- **WHEN** `SNAPSHOTTER_JOB_JSON` is set to a valid JSON object string
- **THEN** Snapshotter parses and validates it and proceeds to execution

#### Scenario: Missing payload fails fast
- **WHEN** `SNAPSHOTTER_JOB_JSON` is not set
- **THEN** Snapshotter fails before cloning or running any pipeline steps

### Requirement: Job schema validation is enforced before execution
Snapshotter MUST validate `SNAPSHOTTER_JOB_JSON` against the existing pydantic `Job` schema before any work begins. The schema MUST retain required fields `repo_url`, `ref`, and `output` (including `output.s3_bucket` and `output.s3_prefix`).

#### Scenario: Invalid schema fails fast
- **WHEN** `SNAPSHOTTER_JOB_JSON` is present but missing required fields (e.g., `repo_url` or `ref` or `output`)
- **THEN** Snapshotter fails before cloning or running any pipeline steps

### Requirement: Default output directory contract is preserved
Snapshotter MUST write artifacts under the existing default directory layout: `out/<repo_slug>/<timestamp_utc>/<job_id>`.

#### Scenario: Outputs land in the expected directory structure
- **WHEN** Snapshotter completes a run for a repo
- **THEN** artifacts are written under `out/<repo_slug>/<timestamp_utc>/<job_id>`

### Requirement: Work directory contract is preserved
Snapshotter MUST continue using `.snapshotter_tmp` as the working directory for cloning and inspection.

#### Scenario: Workdir is located under .snapshotter_tmp
- **WHEN** Snapshotter begins cloning/inspection steps
- **THEN** the working copy resides under `.snapshotter_tmp`

### Requirement: Pass2 requires OPENAI_API_KEY and fails hard if missing
Snapshotter MUST require `OPENAI_API_KEY` for Pass2 semantic analysis and MUST fail hard if it is not present, before any external API call is made.

#### Scenario: Missing OPENAI_API_KEY fails before API usage
- **WHEN** Pass2 semantic analysis is reached and `OPENAI_API_KEY` is not set
- **THEN** Snapshotter terminates with an error before making any API call

### Requirement: Optional dotenv loading remains a convenience feature only
Snapshotter MUST treat `--dotenv` / `--dotenv-override` as a local convenience for loading environment variables. Snapshotter MUST continue to require the job payload via `SNAPSHOTTER_JOB_JSON` in the environment (no alternative payload channels are introduced).

#### Scenario: Dotenv can supply SNAPSHOTTER_JOB_JSON
- **WHEN** `--dotenv` is used and the loaded env includes `SNAPSHOTTER_JOB_JSON`
- **THEN** Snapshotter proceeds using the env-provided payload

### Requirement: Optional S3 upload behavior remains unchanged
If uploads are enabled by configuration, Snapshotter MUST use standard boto3 credential resolution and MUST support region configuration via `--aws-region` or `AWS_REGION` / `AWS_DEFAULT_REGION`. Uploads MUST use server-side encryption `AES256`.

#### Scenario: Upload configuration is taken from the job payload
- **WHEN** the job payload includes `output.s3_bucket` and `output.s3_prefix`
- **THEN** Snapshotter uses those values to determine upload destination

#### Scenario: Region resolution follows existing rules
- **WHEN** `--aws-region` is provided or `AWS_REGION` / `AWS_DEFAULT_REGION` are set
- **THEN** Snapshotter uses that region for S3 operations
