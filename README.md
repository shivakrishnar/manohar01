# Repository status: Java project removed from `main`

The previous Java/Gradle project has been removed from the `main` branch and preserved in a backup branch called `main-java-backup`.

If you're looking for the new Python implementation, switch to the `python` branch — it contains a minimal port of the archiver service (lightweight CLI, fetcher, storage uploaders, DAOs).

If you need to restore or inspect the original Java sources, they are available on the `main-java-backup` branch.

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
