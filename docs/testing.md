# Testing

Ensure all [Prerequisites](#prerequisites) are met and the project has been [Set Up](#set-up) before running tests.

## Running the Full Test Suite

This is the main command you should run before committing code. On macOS and Windows, this will run everything. On Linux, it will run the backend tests and print a warning that the Unity tests are being skipped.

```sh
make test
```

## Running Specific Test Suites

To run only unit tests for all services, use the following command. This is useful for quickly checking for errors.

```sh
make test-unit
```

To run only the integration tests, use this command. These tests take longer to run.

```sh
make test-integration
```

To run only the Unity **Edit Mode** and **Play Mode** tests, use the script below. This requires a local installation of the correct Unity Editor version and can only be run on **macOS or Windows**.

```sh
make test-unity
```

This test suite takes the longest to run, especially if you haven't run it before.

## Running Tests Locally

To run tests locally, see the specific service's `README.md`:

- [Python Services](./developer_guide.python_services.md#local-testing)
- [Web Portal](../web-portal/README.md#local-testing)
- [Unity](../unity/README.md#local-testing)

## Generating a Coverage Report

To generate a coverage report, run:

```sh
make coverage-report
```

This runs all tests locally, aggregates results, and opens the file in the web browser.
