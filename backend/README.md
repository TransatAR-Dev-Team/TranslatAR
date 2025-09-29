# Backend - TranslatAR

This directory contains the backend API gateway for the TranslatAR project. It's a Python application built with FastAPI that orchestrates communication between the frontend, the speech-to-text service, the translation service, and the database. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [MongoDB](https://www.mongodb.com/): A NoSQL database used here to store translation history, accessed via the `motor` async driver.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

### Prerequisites

Python 3.11 must be installed on your system before managing dependencies locally. If you're not altering dependencies, this isn't needed.

* On Ubuntu/Debian-based systems, you can use Dead Snakes to install it:
    ```sh
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3.11-dev
    ```
* On macOS, install via Homebrew:
    ```sh
    brew install python@3.11
    ```
* Windows makes everything harder. This is no different.

## Managing Dependencies

A benefit of Docker is that you can run the backend without a local Python installation. However, when managing dependencies (adding, removing, updating, etc.), it is more stable and reliable to use a local Python virtual environment (`venv`).

Using a local `venv` ensures the `requirements.txt` file—the single source of truth for the project's dependencies—is updated correctly.

The easiest and recommended way to add or update dependencies is as follows:

> The following instructions are for macOS/Linux. Windows users, you're on your own.

1.  **Create and activate a virtual environment.** From this directory, run:
    ```sh
    # Create the venv
    python3.11 -m venv .venv

    # Activate it:
    source .venv/bin/activate
    ```
    
    Activating the `.venv` ensures that the `pip` command you use is the one inside it, not a global one. You can check with `which pip`. It should output something like:

    ```log
    # Inside the venv:
    /path/to/repo/TranslatAR/backend/.venv/bin/pip
    ```

2.  **Sync your local environment.** Before adding a new package, ensure your `venv` is aligned with the project's requirements file.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install or uninstall the new dependency.**
    ```bash
    # Example install
    pip install <package-name>

    # Example uninstall
    pip uninstall <package-name>
    ```

4.  **Update the requirements file.** After making changes, "freeze" the current state of all packages in your `venv` into the `requirements.txt` file.
    ```bash
    pip freeze > requirements.txt
    ```

5.  **Commit the updated `requirements.txt` file.**
    ```bash
    git add requirements.txt
    git commit
    ```
6. Deactivate the `venv`:
    ```bash
    deactivate
    ```

    > **IMPORTANT:** The `.venv/` directory ***should never be committed.*** We use `git` to keep track of the dependency list, not the installed packages themselves. This keeps the repository small and portable.

    > `.venv` and `__pycache__/` can be safely deleted after committing: `rm -rf .venv __pycache__/`.

This process ensures that when another developer (or the Docker build process) installs dependencies, they will get the exact same versions you used.
