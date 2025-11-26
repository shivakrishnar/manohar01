# Repository (python branch): Java files removed from this branch

The `python` branch only contains a Python port of the original project under the `python/` directory.

If you need the original Java project it has been preserved in the `main-java-backup` branch (or check `main` for the latest state before cleanup).

Files remaining in this branch:

- python/ (Python port and example config)
- README.md (this file)
- .github/, .gitignore, and VS Code settings for repository metadata

Run the Python port from the `python/` directory as described in `python/README.md`.

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
