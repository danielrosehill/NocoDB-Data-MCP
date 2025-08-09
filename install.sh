#!/bin/bash
# Installation script for NoCoDB MCP Server

set -e

echo "Installing NoCoDB MCP Server..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing nocodb-mcp in development mode..."
pip install -e .

echo "Installation complete!"
echo ""
echo "To use the MCP server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the server: python -m nocodb_mcp.server"
echo ""
echo "Or add this to your MCP client configuration:"
echo "  Command: $(pwd)/venv/bin/python"
echo "  Args: ['-m', 'nocodb_mcp.server']"
echo "  Cwd: $(pwd)"
