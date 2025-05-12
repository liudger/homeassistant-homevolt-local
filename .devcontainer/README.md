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

PyCharm Professional supports working with Dev Containers directly. Here's how to set it up:

1. Open the project in PyCharm Professional.
2. Go to File > Settings > Build, Execution, Deployment > Docker.
3. Click the "+" button to add a new Docker configuration.
4. Set up the connection to your Docker daemon (usually just accepting the defaults works).
5. Click "Apply" and "OK".
6. Go to File > Remote Development > Dev Containers.
7. Click "Open in Dev Container".
8. PyCharm will build the container based on the devcontainer.json configuration and open the project inside it.
9. PyCharm will now use the Docker container for code execution, debugging, etc.

Note: PyCharm's Dev Container support uses the same devcontainer.json configuration file as VS Code, so there's no need for a separate docker-compose.yml file.

## Customizing the Environment

- To add more Python packages, edit the Dockerfile and add them to the `pip install` command.
- To add more system packages, edit the Dockerfile and add them to the `apt-get install` command.
- To change environment variables, edit the devcontainer.env file.
- To customize VS Code settings, edit the "vscode" section in devcontainer.json.
- To customize PyCharm settings, edit the "jetbrains" section in devcontainer.json.
