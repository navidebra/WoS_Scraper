#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Print each command before executing it (for debugging purposes)
set -x

# Install Python dependencies using pip
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build the frontend (if applicable)
npm run build

# Run any additional build steps here
# For example, if you need to compile or transpile files, you can do that here

echo "Build script completed successfully."
