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
