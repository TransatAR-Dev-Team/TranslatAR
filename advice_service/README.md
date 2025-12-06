# Advice Service - TranslatAR

This directory contains the advice generation microservice for the TranslatAR project. It's a Python application built with FastAPI that acts as a gateway to a large language model (LLM) provider. It receives a conversation transcript, formats a prompt for a language coach persona, and returns constructive advice. It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.11.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [Ollama](https://ollama.com/): A tool for running large language models locally. This service forwards requests to an Ollama container.
- [Docker](https://www.docker.com/): A containerization tool, allowing the service to run in an isolated and consistent environment.

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

For details on managing Python dependencies and setting up a local testing environment, please see the [Python Services - Development Guide](../docs/developer_guide.python_services.md).
