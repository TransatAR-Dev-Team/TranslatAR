# Dev Containers in VS Code

Quick guide to set up and run Dev Containers in Visual Studio Code.

## Initial Setup

### Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
   - Ensure Docker is running before using dev containers
2. **Visual Studio Code** - [Download here](https://code.visualstudio.com/)
3. **Dev Containers Extension**
   - Open VS Code Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`)
   - Search for "Dev Containers" and install the extension by Microsoft

## Adding a Dev Container to Your Project

1. Open your project folder in VS Code
2. If there is already a docker-compose.yml (there is in our case), create a .devcontainer directory in the root dir
3. Inside that .devcontainer, create a devcontainer.json, for multiple different containers, separate them in respective directories inside .devcontainer

## Configuration

Your `.devcontainer/devcontainer.json` file defines your container environment:

```json
{
  "name": "Backend",
  "dockerComposeFile": "../../docker-compose.yml",
  "service": "backend",
  "workspaceFolder": "/app"
}
```

**Key properties:**
- `name` - Display name for your container
- `dockerComposeFile` - The name of the docker-compose file(s) used to start the services.
- `service` - The name of the container you want to run (this is also located in the docker-compose.yml)
- `workspaceFolder` - The path of the workspace folder inside the container. This is typically the target path of a volume mount in the docker-compose.yml.

## Opening Your Project in a Container

1. Press `F1`
2. Type: `Dev Containers: Reopen in Container`

The first build may take a few minutes. Once connected, your terminal and VS Code will run inside the container.
