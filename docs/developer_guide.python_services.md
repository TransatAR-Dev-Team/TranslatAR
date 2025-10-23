# Python Services - Development Guide

This guide provides common instructions for setting up and managing the Python-based microservices within the TranslatAR project, including the `backend`, `stt-service`, `translation-service`, and `summarization-service`.

## Prerequisites

1. A specific version of Python is required for local testing and dependency management for each service. Please refer to the service's specific `README.md` to ensure you have the correct version installed (`stt-service` uses `3.10`, all others use `3.11`).

    If you do not have the required version, you can use the following methods:

    - **On Ubuntu/Debian-based systems**, you can use the `deadsnakes` PPA:

        ```sh
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt update
        # Example for Python 3.11
        sudo apt install python3.11 python3.11-venv python3.11-dev
        ```

    - **On macOS**, you can use [Homebrew](https://brew.sh/):

        ```sh
        # Example for Python 3.11
        brew install python@3.11
        ```

    - **On Windows**, you can use [pyenv-win](https://github.com/pyenv-win/pyenv-win).

2. **Poetry**: You must have the Python package manager [Poetry installed](https://python-poetry.org/docs/#installation).

## Local Testing

1. Ensure [prerequisites](#prerequisites) are met.

2. `cd` into the service's directory.

    ```sh
    # For example:
    cd backend
    ```

3. Install all dependencies:

    ```sh
    poetry install
    ```

4. Run the tests:

    ```sh
    poetry run pytest -v
    ```

## Formatting and Linting

We use **Black** for code formatting and **Ruff** for linting and import sorting.

1.  **Navigate to the service directory** (e.g., `cd backend`).

2.  To format your code, run:

    ```sh
    poetry run black .
    poetry run ruff format .
    ```

3.  To lint your code and automatically fix any issues, run:

    ```sh
    poetry run ruff check . --fix
    ```

You can also format and lint all services at once from the project root using `make format` and `make lint`.

## Managing Dependencies with Poetry

> The following instructions are for macOS/Linux.

This workflow applies to every Python service in this repository.

1. **Navigate to the service directory.** All `poetry` commands must be run from the directory containing the service's `pyproject.toml` file.

    ```sh
    # Example
    cd backend
    ```

2. **Install Project Dependencies.** To add or remove packages, run the following commands from the service's root directory.

    Add a new production dependency:

    ```bash
    poetry add <package-name>
    ```

    Add a development-only dependency (e.g., a linter, test dependencies):
    
    ```sh
    poetry add --group dev <package-name>
    ```

    Remove a dependency:

    ```sh
    poetry remove <package-name>
    ```

3. **Commit Your Changes.** After you have modified dependencies, the `pyproject.toml` and `poetry.lock` files must be committed. These two files are the single source of truth for the project's dependencies.

    ```sh
    git add pyproject.toml poetry.lock
    git commit -m "<commit message>"
    ```
