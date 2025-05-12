# Development Container for Homevolt Local Integration

This directory contains configuration files for setting up a development container for the Homevolt Local integration. The development container provides a consistent development environment with all the necessary tools and dependencies pre-installed.

## What's Included

- Python 3.13.2 environment
- Development tools: black, pylint, pytest, mypy, isort
- Git, curl, wget, vim
- All project dependencies installed from requirements.txt and requirements-dev.txt

## Using with VS Code

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code.
2. Open the project folder in VS Code.
3. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container".
4. VS Code will build the container and open the project inside it.

## Using with PyCharm

PyCharm Professional supports working with Docker-based development environments. Here's how to set it up:

1. Open the project in PyCharm Professional.
2. Go to File > Settings > Build, Execution, Deployment > Docker.
3. Click the "+" button to add a new Docker configuration.
4. Set up the connection to your Docker daemon (usually just accepting the defaults works).
5. Click "Apply" and "OK".
6. Go to File > Settings > Project: homeassistant-homevolt > Python Interpreter.
7. Click the gear icon and select "Add...".
8. Choose "Docker Compose" from the left panel.
9. Configure:
   - Server: Select the Docker connection you just created
   - Configuration file(s): Browse to the docker-compose.yml file (you may need to create one, see below)
   - Service: Select the service from your docker-compose file
10. Click "OK" to create the interpreter.
11. PyCharm will now use the Docker container for code execution, debugging, etc.

### Creating a docker-compose.yml file

For PyCharm integration, you might need to create a docker-compose.yml file at the root of your project:

```yaml
version: '3'
services:
  dev:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - .:/workspaces/homeassistant-homevolt
    env_file:
      - .devcontainer/devcontainer.env
    command: sleep infinity
```

## Customizing the Environment

- To add more Python packages, edit the Dockerfile and add them to the `pip install` command.
- To add more system packages, edit the Dockerfile and add them to the `apt-get install` command.
- To change environment variables, edit the devcontainer.env file.
- To customize VS Code settings, edit the "vscode" section in devcontainer.json.
- To customize PyCharm settings, edit the "jetbrains" section in devcontainer.json.