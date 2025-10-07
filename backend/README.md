# Backend - TranslatAR

This directory contains the backend API gateway for the TranslatAR project. It's a Python application built with FastAPI that orchestrates communication between the frontend, the speech-to-text service, the translation service, and the database. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [MongoDB](https://www.mongodb.com/): A NoSQL database used here to store translation history, accessed via the `motor` async driver.
- [Pytest](https://docs.pytest.org/en/stable/): Python testing framework.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.

## Getting Started

For complete setup instructions, including how to build and run the entire project with Docker, please see the `README.md` in the root of the project.

### Local Development

For tasks such as managing dependencies or running tests outside of Docker, this service requires Python 3.11.

For detailed instructions on setting up a Python environment, managing dependencies with `pip`, and running tests locally with `pytest`, please refer to the **Developer Guide** in the [root `README.md`](../README.md#developer-guide).
