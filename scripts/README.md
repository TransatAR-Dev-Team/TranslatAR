# Scripts - TranslatAR

This folder contains shell and Python scripts used by the project. The primary way to interact with these scripts is via the top-level [`Makefile`](../Makefile) (see [README - Common Commands](../README.md#common-commands)).

## Prerequisites

All project [Prerequisites](../README.md#prerequisites) met.

## Usage

- Prefer: `make <target>` from the repository root. The `Makefile` delegates to the scripts in this directory.
- Direct: run a script with `./scripts/<script-name>` (or `python scripts/<python-script-name>.py`) from the repo root.

## Scripts

- [`docker-compose-manager.sh`](./docker-compose-manager.sh): Wrapper around `docker-compose` that auto-detects GPU, forwards common arguments, and is used by `Makefile` targets like `up`, `down`, `logs`, and `restart`.

- [`format.sh`](./format.sh): Runs project formatters (e.g. Black, Ruff formatter for Python, Prettier for frontend). Use `make format` to run across the repo.

- [`lint.sh`](./lint.sh): Runs linters (Ruff for Python, ESLint for web). Use `make lint` or run directly.

- [`open_unity_editor.sh`](./open_unity_editor.sh): Convenience script to open the Unity editor for the `unity/` project on macOS/Windows. Run via `make unity-editor` (macOS/Windows only).

- [`run_all_tests.sh`](./run_all_tests.sh): Orchestrates all test suites (unit, integration, and Unity tests where applicable). Called by `make test`. The script will exit with an error if any test fails, making it suitable for CI/CD pipelines.

- [`run_integration_tests.sh`](./run_integration_tests.sh): Runs backend integration tests (uses Docker where appropriate). Use `make test-integration`.

- [`run_unit_tests.sh`](./run_unit_tests.sh): Runs unit tests for components/services in the workspace. Use `make test-unit`.

- [`run_unity_tests.sh`](./run_unity_tests.sh): Runs Unity tests (editor or playmode). Use `make test-unity` on supported OS.

- [`parse_unity_results.py`](./parse_unity_results.py): Python helper to parse Unity test results or other Unity-produced files into a consumable format. Helper script to `run_unity_tests.sh`.


## Notes & tips

- If a script isn't executable locally, make it so with:

    ```sh
    chmod +x scripts/*.sh
    ```

- Some scripts assume Docker is running and will crash if it is not.

- Linting and formatting scripts expect Python and `npm` prerequisites to be met.
