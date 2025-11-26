# Python port of dex-trigger-response-archive

This folder contains a lightweight Python port of the Java application present on the `main` branch.

Quick start

1. Create and activate a virtualenv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Provide configuration (example `config.yaml` is included).

3. Run the small CLI tool:

```bash
python -m pyarchiver.archiver_app config.yaml
```

Notes

- This port mirrors the Java structure (simplified) with: ArchiverApp (CLI), ArchiverService, TriggerFetcher, TokenProvider, DAOs, and storage uploaders.
- The S3 uploader uses `boto3`.
- The Python implementation is intentionally minimal — a drop-in skeleton to make migration and testing easier.

Packaging
---------

The repository includes a ``pyproject.toml`` in `python/` so you can build standard Python artifacts (wheel + sdist).

Local build example (recommended in a venv):

```bash
python3 -m pip install --upgrade build
cd python
./build.sh
```

Artifacts will be written to `python/dist/`.
