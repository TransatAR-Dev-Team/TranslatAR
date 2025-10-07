# Translation Service - TranslatAR

This directory contains the translation microservice for the TranslatAR project. It is a Python application built with FastAPI that forwards translation requests to a LibreTranslate instance. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [LibreTranslate](https://libretranslate.com/): An open-source machine translation API. This service acts as a gateway to it.
- [httpx](https://www.python-httpx.org/): An async HTTP client used to forward requests to LibreTranslate.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.
- [Pytest](https://docs.pytest.org/en/stable/): Python testing framework.

## Getting Started

For complete setup instructions, including how to build and run the entire project with Docker, please see the `README.md` in the root of the project.

### Local Development

For tasks such as managing dependencies or running tests outside of Docker, this service requires Python 3.11.

For detailed instructions on setting up a Python environment, managing dependencies with `pip`, and running tests locally with `pytest`, please refer to the **Developer Guide** in the [root `README.md`](../README.md#developer-guide).
