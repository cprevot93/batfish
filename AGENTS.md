# Batfish — Agent Guide

## Build system

- **Bazel** (with Bzlmod), NOT Maven. Requires `bazelisk` (v9.1.0 per `.bazelversion`).
- Java 17 required for both build and runtime.
- Dependencies in `MODULE.bazel`; lockfile at `maven_install.json`.
- After changing a dependency run: `REPIN=1 bazel run @maven//:pin`

## Key commands

```bash
bazel build //...                                    # build all
bazel test //...                                     # all tests (slow)
bazel test --test_output=errors //projects/batfish/...  # tests for one module
bazel test --test_filter=MyClass#myMethod //path/to:tests  # single test method
bazel test --nocache_test_results //path/to:tests    # force re-run
bazel test --test_tag_filters=-pmd_test //...        # skip PMD static analysis
bazel coverage //...                                 # coverage (uses JaCoCo)
tools/bazel_run.sh                                   # build & run allinone locally
tools/bazel_run.sh -d                                # with debugger on port 5009
./tools/update_refs.sh                               # auto-update reference test files
```

## Pre-commit hooks (required)

```bash
pip install pre-commit && pre-commit install
```

Runs: `google-java-format`, `buildifier` (Bazel lint), `black`, `isort`, `autoflake`.

## Project structure (monorepo under `projects/`)

| Directory        | Role                                                        |
|------------------|-------------------------------------------------------------|
| `allinone`       | Entrypoint bundling coordinator + worker + client in one JVM|
| `batfish`        | Core engine: parsing, conversion, dataplane, BDD analysis   |
| `common`         | Vendor-independent data model, utilities, plugin framework  |
| `coordinator`    | REST API (Grizzly/Jersey), work queue, auth                 |
| `client`         | Java CLI client                                              |
| `question`       | ~60 question plugins (reachability, traceroute, etc.)       |
| `minesweeper`    | Grammar-based security analysis (BDD regex)                 |
| `bdd`            | JavaBDD library wrapper                                     |
| `symbolic`       | Symbolic analysis utilities                                 |

`projects/VERSION`: `0.36.0`

## Key entrypoints

- `//projects/allinone:allinone_main` — local dev runner (used by `tools/bazel_run.sh`)
- `org.batfish.coordinator.Main` — REST service
- `org.batfish.main.Driver` — Batfish worker init
- `org.batfish.main.Batfish` — core engine pipeline

## Test organization

Three kinds of tests:

1. **JUnit 4 unit tests** — alongside source at `projects/<module>/src/test/java/`. Auto-discovered via `junit_tests` macro. Hamcrest matchers strongly preferred over `assertEquals`/`assertTrue`.
2. **Reference tests** — `tests/` directory: client `commands` + `.ref` expected output. Run via `bazel test //tests/...`.
3. **PMD tests** — static analysis per subproject. Tagged `pmd_test`; can be excluded with `--test_tag_filters=-pmd_test`.

All test targets require `--explicit_java_test_deps` (enforced in `.bazelrc`).

## Framework quirks

- **ANTLR4** — grammar files in `projects/batfish/src/main/antlr4/`. Codegen via `antlr.bzl` Starlark rule.
- **BDD memory is manual** — JavaBDD uses reference counting via `BDDFactory`, NOT GC. See `docs/development/bdd_best_practices.md`.
- **AutoService / AutoValue** — annotation processors for plugin registration and value classes. Plugins registered via `@AutoService` in `projects/question/`.
- **Parboiled parsers** — used for Juniper and Check Point; excluded from coverage instrumentation (see `.bazelrc`).
- **Checkstyle** — enforces import bans (`com.google.common.io.Files`, `org.hamcrest.CoreMatchers`, etc.), annotation placement rules. Run via `tools/run_checkstyle.sh`.

## Pipeline (inside `Batfish.java`)

```
Parse (ANTLR4) → Extract (vendor objects) → Convert (to VI model) → Post-process → Dataplane (IBDP) → Answer questions
```

## CI order (`.github/workflows/pre-commit.yml`)

`format` → `json_template` → `checkstyle` → `bazel build/test` → `coverage`

Replicate this order locally before pushing.

## Style

- Google Java style (2-space indent, 100-char line limit). Enforced by `google-java-format`.
- `@Nullable`/`@Nonnull` on the type line (enforced by Checkstyle).
- No wildcard imports, no unused imports (Error Prone).
- Commit messages: `type(scope): subject` preferred.
