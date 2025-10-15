# Backend - TranslatAR

This directory contains the backend API gateway for the TranslatAR project. It's a Python application built with FastAPI that orchestrates communication between the frontend, the speech-to-text service, the translation service, and the database. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [MongoDB](https://www.mongodb.com/): A NoSQL database used here to store translation history, accessed via the `motor` async driver.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

For details on managing Python dependencies and setting up a local development environment, please see the [Python Services - Development Guide](../docs/developer_guide.python_services.md).
