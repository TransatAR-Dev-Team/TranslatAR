# Code Quality

To ensure code consistency and quality, this project uses `pre-commit` to run checks and automatically make changes on each file you commit. These checks include formatters and linters such as:

- **Python Services**: Formatted with **Black** and linted with **Ruff**.
- **Web Portal**: Formatted with **Prettier** and linted with **ESLint**.
- **Security**: Secret detection to prevent committing credentials.
- **General**: Checks for whitespace, file endings, and other common issues.

The full configuration can be found in the [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) file.

## When a commit is rejected

If your `git commit` is blocked, it means the hooks caught an issue. There are two scenarios.

1. **The hooks have made automatic changes to your files.**

    A formatter has fixed your code for you. Stage the changes and try to commit again.

    ```sh
    git add .
    git commit
    ```

2. **The errors need a manual fix.**

    Read the error messages carefully. It will tell you the file, line number, and what is wrong. Fix the error, stage the files, and commit again.

    > **Important:** If a secret is detected, **you must remove it.** Do not add it to the baseline file unless you are 100% certain that it is a false positive.

### Running Checks Manually

You can run these checks at any time without creating a commit.

**Using `pre-commit`:**

To run on only staged files:

```sh
pre-commit run
```

To run on any modified files (staged or not)

```sh
pre-commit run --files $(git ls-files -m)
```

To run on all files:

```sh
pre-commit run --all-files
```

**Using `make`:**

To format and lint all code:

```sh
make validate
```

To format all code:

```sh
make format
```

To lint all code:

```sh
make lint
```

For instructions on running  tools within a specific service, see the developer guides for [Python services](./developer_guide.python_services.md#formatting-and-linting) and the [Web Portal](../web-portal/README.md#formatting-and-linting).
