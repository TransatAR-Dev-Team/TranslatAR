# Translation Service - TranslatAR

This directory contains the translation microservice for the TranslatAR project. It is a Python application built with FastAPI that forwards translation requests to a LibreTranslate instance. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [LibreTranslate](https://libretranslate.com/): An open-source machine translation API. This service acts as a gateway to it.
- [httpx](https://www.python-httpx.org/): An async HTTP client used to forward requests to LibreTranslate.

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

For details on managing Python dependencies and setting up a local testing environment, please see the [Python Services - Development Guide](../docs/developer_guide.python_services.md).
