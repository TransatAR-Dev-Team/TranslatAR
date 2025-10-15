# Speech-To-Text Service - TranslatAR

This directory contains the speech-to-text (STT) microservice for the TranslatAR project. It is a Python application built with FastAPI that exposes an API for audio transcription. The service uses faster-whisper, an optimized implementation of OpenAI’s Whisper model, and can run on either CPU or GPU (CUDA). It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.10.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): Efficient Whisper implementation for speech recognition.
- [Docker](https://www.docker.com): A containerization tool, allowing the service to run in an isolated and consistent environment.
- [CUDA/cuDNN](https://developer.nvidia.com/cuda-zone): Used for GPU acceleration if available.

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project, including enabling GPU acceleration for STT.

For details on managing Python dependencies and setting up a local development environment, please see the [Python Services - Development Guide](../docs/developer_guide.python_services.md).
