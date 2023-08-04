#!/bin/bash
set -euo pipefail

# Replace '-' with '_' in project name
KERNEL_NAME="python-chartsworth-dev"
DISPLAY_NAME="Python (chartsworth-dev)"

# Install the IPython kernel
poetry run python -m ipykernel install --user --name="$KERNEL_NAME" --display-name="$DISPLAY_NAME"

echo "Installed kernel $KERNEL_NAME for the Chatlab Development Environment"
