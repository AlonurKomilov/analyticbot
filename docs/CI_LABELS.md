# CI Labels Guide

This project uses GitHub labels to control the behavior of the Continuous Integration (CI) pipeline. This allows for flexible and explicit policy control on a per-pull-request basis.

## Available Labels and Their Functions

- `mypy:softfail`:
  - **Function:** Makes the `MyPy` type-checking job non-blocking. If MyPy finds type errors, the check will still pass, but the errors will be visible in the logs.
  - **Use Case:** Useful for pull requests that introduce legacy code or code with complex type issues that cannot be resolved immediately. This allows the PR to be merged without blocking on type-checking, with the understanding that the type errors will be fixed later.

- `cov:27` / `cov:50`:
  - **Function:** Sets the minimum required code coverage threshold for the tests. The CI will fail if the coverage is below the specified percentage.
    - `cov:27`: Sets the threshold to 27%.
    - `cov:50`: Sets the threshold to 50%.
  - **Default:** If no `cov:` label is present, the coverage threshold defaults to a strict `70%`.
  - **Use Case:** Lowering the coverage threshold can be necessary for initial PRs, refactoring efforts, or when testing is difficult. It provides a way to merge code while explicitly acknowledging the current test coverage level.

- `compose-verify:on`:
  - **Function:** Triggers an additional CI workflow (`compose-verify.yml`) that builds and runs the entire application stack using Docker Compose. This workflow runs database migrations and performs a smoke test to ensure the system is operational.
  - **Use Case:** This should be used for pull requests that make significant changes to the backend, database schemas, or Docker setup. It provides a higher level of confidence that the application runs correctly in a production-like environment.

- `automerge`:
  - **Function:** Enables automatic merging of the pull request once all required CI checks have passed. This is handled by the Mergify app (if installed).
  - **Use Case:** Ideal for non-critical changes, dependency updates, or any PR that you are confident can be merged without further manual review once the automated checks are green.

## Examples of Label Combinations

- **PR with legacy code needing a relaxed policy:**
  - `mypy:softfail` + `cov:27` + `compose-verify:on`
  - *Result:* MyPy won't block the merge, the coverage requirement is low, and the full Docker Compose stack is verified.

- **PR with a strict policy (default behavior):**
  - *(No labels)*
  - *Result:* MyPy is a required check, and the coverage threshold is 70%.

- **PR ready for deployment:**
  - `automerge` + `compose-verify:on`
  - *Result:* The full system is verified, and the PR will be merged automatically as soon as all checks pass.
