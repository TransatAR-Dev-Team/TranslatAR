# Speech-To-Text Service - TranslatAR

This directory contains the speech-to-text (STT) microservice for the TranslatAR project. It is a Python application built with FastAPI that exposes an API for audio transcription. The service uses `faster-whisper`, an optimized implementation of OpenAI’s Whisper model, and can run on either CPU or GPU (CUDA). It is containerized with Docker.

## Tech Stack

- [Python](https://www.python.org/): **Version 3.10.**
- [FastAPI](https://fastapi.tiangolo.com/): A modern, high-performance Python web framework for building APIs.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): Efficient Whisper implementation for speech recognition.
- [Pytest](https://docs.pytest.org/en/stable/): Python testing framework.
- [Docker](https://www.docker.com): A containerization tool, allowing the service to run in an isolated and consistent environment.
- [CUDA/cuDNN](https://developer.nvidia.com/cuda-zone): Used for GPU acceleration if available.

## Getting Started

For complete setup instructions, including how to build and run the entire project with Docker, please see the `README.md` in the root of the project.

### Local Development

For tasks such as managing dependencies or running tests outside of Docker, this service requires **Python 3.10**.

For detailed instructions on setting up a Python environment, managing dependencies with `pip`, and running tests locally with `pytest`, please refer to the **Developer Guide** in the [root `README.md`](../README.md#developer-guide).
