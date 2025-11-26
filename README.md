# DAO Java Gradle Project

This project is a minimal Java 17 Gradle project demonstrating a simple DAO pattern with an in-memory implementation and unit tests.

Project layout:

- `build.gradle` - Gradle build file
- `settings.gradle` - project name
- `src/main/java/com/example/...` - application and DAO implementation
- `src/test/java/...` - JUnit 5 tests

Quick start

1. Ensure you have Java 17 and Gradle installed (or use the Gradle wrapper if added).

2. Build and run tests:

```bash
cd dao-gradle-project
./gradlew test   # if you have the wrapper
# or with system gradle
gradle test
```

3. Run the application:

```bash
gradle run
```

Notes

- The DAO lives in `com.example.dao`. `InMemoryUserDao` is thread-safe and backed by a `ConcurrentHashMap`.
- Tests use JUnit 5 (Jupiter).

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
