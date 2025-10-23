# Web Portal - TranslatAR

This directory contains the frontend web portal for the TranslatAR project. It's a web app built with Vite, React, and TypeScript, styled with Tailwind CSS, and containerized with Docker.

## Tech Stack

- [Vite](https://vite.dev/): A frontend build tool that provides an extremely fast development server and optimized builds. Hot Module Replacement (HMR) is configured, so any changes made within the `src` directory while the app is running will immediatly be reflected in the UI.

- [React](https://react.dev/): A component-based JavaScript library for building UI.

- [TypeScript](https://www.typescriptlang.org/): A superset of JavaScript that adds typing.

- [Tailwind CSS](https://tailwindcss.com/): A CSS framework for rapidly building custom user interfaces without writing custom CSS.

- [Docker](https://www.docker.com/): A containerization tool, allowing it to run in an isolated and consistent environment across any machine and to be easily depoloyed to production.

## Getting Started

See more detail in `README.md` in the root of the project for instructions on building and runnning the entire project.

## Local Testing

This project uses Vitest for unit and component testing.

1. Ensure you have Node.js and npm installed locally.
2. Install all dependencies:

    ```bash
    npm install
    ```

3. Run the test suite:

    ```bash
    npm test
    ```

    To run continuously and watch for changes, use:

    ```bash
    npm run test:watch
    ```

## Managing Dependencies

A benefit of Docker is that you can run the web portal without installing Node.js or any dependencies on your local machine. However, when it comes to managing those dependencies (adding, removing, updating, etc), it is more stable and reliable to use `npm` locally.

Running `npm install <package-name>` on your local machine correctly updates `package.json` and `package-lock.json`. These two files are the single source of truth of the web portal's dependencies.

The easiest and recommended way to add or update dependencies is as follows:

1. Ensure you have Node.js (and therefore `npm`) [installed](https://nodejs.org/en/download). 

2. Before installing a new package, ensure your local node_modules directory is aligned with the project's lock file. Run this command inside the web-portal directory:

    ```sh
    npm install
    ```
  
3. Install the new dependency.

    For a runtime dependency:

    ```sh
    npm install <package-name>
    ```

    For a development dependency (e.g., a linting tool, testing framework):

    ```sh
    npm install -D <package-name>
    ```

    This also applies for `npm uninstall`.

4. Commit `package.json` and `package-lock.json`.

    ```sh
    # Additional files may be added, of course
    git add package.json package-lock.json
    git commit
    ```

    > `node_modules/` can be safely deleted after this step: `rm -rf node_modules`.

    VSCode's source control interface (and other GUI apps) may alse be used.

    > **IMPORTANT:** The `node_modules/` directory ***should never be committed.*** We use `git` keep track of the dendency lists, not the dependencies themselves. This will keep our repository as small and portable as possible.

This ensures that when another developer (or the Docker build process) runs `npm install`, they will get the exact same dependency tree you have. 
