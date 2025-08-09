#!/bin/bash
# Run NoCoDB MCP Server in foreground (stops when terminal closes)

set -e

echo "🚀 Starting NoCoDB MCP Server (foreground mode)..."
echo "Press Ctrl+C to stop the server"
echo "Server will stop when you close this terminal"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if server module exists
if ! python -c "import nocodb_mcp.server" 2>/dev/null; then
    echo "❌ MCP server not found. Running installation..."
    ./install.sh
fi

# Start the server
echo "Starting MCP server..."
echo "Listening for MCP protocol messages on stdin/stdout..."
echo ""

# Run the server (this will block and wait for MCP messages)
python -m nocodb_mcp.server
