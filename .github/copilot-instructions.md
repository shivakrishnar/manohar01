<!--
This file guides AI coding agents (Copilot / coding agents) to be productive in this repository.
The repo currently contains no discovered code (empty workspace scan). This document is a concise,
actionable template — update placeholders after you add project files so agents can be specific.
-->

# Copilot Instructions for this Repository

Purpose: quickly orient AI coding agents to discover, analyze, and modify this repository with
minimal back-and-forth. Keep this file up-to-date as the project grows.

1) Quick repo check (first actions)
- Run: `ls -la` and `git status` to confirm workspace contents.
- Search for language/config files: `rg "package.json|pyproject.toml|requirements.txt|Dockerfile|Makefile|README.md" || true`.
- If the repo remains empty, report that to the human and request the main entrypoint or sample files.

2) Big-picture discovery steps (how to understand the architecture)
- Look for top-level folders: `src/`, `cmd/`, `app/`, `services/`, `api/`, `web/`, `infrastructure/`.
- Find runtime manifests: `Dockerfile`, `docker-compose.yml`, `k8s/`, `iac/` (Bicep/Terraform/Bicep).
- If present, open `README.md` and any `docs/` for architecture notes; prefer humans' docs over assumptions.

3) Critical files & patterns to scan first
- Dependency manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` — used to infer build/test commands.
- Entrypoints: look for `main()` functions or `server`/`app` startup scripts in `src/`.
- Tests: `tests/`, `spec/`, `__tests__` — use to infer testing commands.
- CI: `.github/workflows/*.yml` — inspect for build/test/deploy steps and reproduce locally if needed.

4) Build, run & test heuristics (examples)
- Node.js: `npm install` then `npm test` or `npm run build` if `package.json` present.
- Python: create venv, `pip install -r requirements.txt` or `pip install -e .`, then `pytest` if present.
- Docker: `docker build -t repo:dev .` and `docker run --rm -p 8080:8080 repo:dev` if `Dockerfile` exists.
- If none of the above files exist, ask the human for the intended runtime and dev commands.

5) Project-specific conventions and examples
- Add here concrete patterns discovered in the repo. Example placeholders to replace once files exist:
  - "API modules live in `src/api/*`; handlers register routes in `src/api/index.ts`"
  - "Database migrations live under `migrations/` and are run with `alembic upgrade head`"

6) Integration points & external dependencies
- Note external services from code/config: e.g., `REDIS_URL`, `DATABASE_URL`, cloud SDKs, message brokers.
- Prefer reading `.env.example`, `env/*`, or `infrastructure/*` to locate required external services.

7) Editing, tests and PR workflow
- Make small, focused changes and run the project's tests (if any). Commit with conventional messages.
- If `.github/workflows` exists, follow the CI matrix (node/python/go) and mirror critical steps locally.

8) What to do when information is missing
- If the repository is empty or lacks clear build instructions, ask the human for:
  - the primary language/runtime, the main entrypoint, and preferred build/test commands
  - sample data or a minimal runnable example
- Offer to create a minimal `README.md` and a small runnable example if allowed.

9) How to update this file
- Keep this document short (20–50 lines). When a new pattern or top-level folder appears, add a
  one-line note and a short example command showing how to build/run that component.

10) Contact & feedback
- If uncertain about any change, leave a draft PR and ask maintainers for the intended behavior.

---
Notes for maintainers: this repository appeared to have no code files during the scan. Update this
file with project-specific examples (replace placeholders) to make future AI agents immediately productive.
