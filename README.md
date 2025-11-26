# dex-trigger-response-archive — Python port (main branch)

This repository now uses a lightweight Python port of the original Java archiver. The Python implementation lives under the `python/` folder and is the primary code on `main` after the merge.

If you still need the original Java code, it's preserved in the `main-java-backup` branch.

What's in this repo now

- `python/` — Python port of the archiver (CLI, service, fetcher, storage uploaders, DAOs)
- `.github/`, `.gitignore`, `.vscode/` — repo metadata and CI/editor configs

Quick start (run the Python port)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and run the small CLI using the sample config:

```bash
pip install -r python/requirements.txt
PYTHONPATH=python/src python3 -m pyarchiver.archiver_app python/config.yaml
```

Outputs from a run are written under `python/archives` and the run summary is `python/output/last_run_summary.json`.

More details about the Python port and how to extend it are in `python/README.md`.

