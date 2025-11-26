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

Build outputs and JSON manifest
--------------------------------

When you run a standard Gradle build the project will produce these main outputs under /build:

- Compiled classes: build/classes/java/main
- Resource files: build/resources/main
- Packaged JAR: build/libs/dex-trigger-response-archive-1.0.0.jar
- Test reports/results: build/test-results/ and build/reports/

Starting with this repository, the build also generates a JSON manifest describing the important build artifacts. The manifest is written to:

```
build/outputs/outputs.json
```

Run the build to create the manifest:

```bash
./gradlew clean build
```

Example manifest keys:
- project — project name
- version — project version
- outputs.jar — path to the main JAR
- outputs.classesDir — path to compiled classes
- outputs.resourcesDir — path to runtime resources

This JSON file is useful for scripts, CI, or other tools that need to know where the build artifacts are located.

---

Note: `main` branch now contains the repository maintenance files only. The Java implementation has moved to `main-java-backup` and the Python port lives on `python`.
