#!/bin/bash
# Run NoCoDB MCP Server in background (keeps running after terminal closes)

set -e

PROJECT_DIR="$(dirname "$0")"
PID_FILE="$PROJECT_DIR/mcp_server.pid"
LOG_FILE="$PROJECT_DIR/mcp_server.log"

start_server() {
    echo "🚀 Starting NoCoDB MCP Server (background mode)..."
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Check if already running
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "❌ Server is already running (PID: $(cat "$PID_FILE"))"
        echo "Use './run_server_background.sh stop' to stop it first"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if server module exists
    if ! python -c "import nocodb_mcp.server" 2>/dev/null; then
        echo "❌ MCP server not found. Running installation..."
        ./install.sh
    fi
    
    # Start server in background
    echo "Starting MCP server in background..."
    nohup python -m nocodb_mcp.server > "$LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    echo "✅ Server started successfully!"
    echo "   PID: $(cat "$PID_FILE")"
    echo "   Log file: $LOG_FILE"
    echo "   Use './run_server_background.sh stop' to stop"
    echo "   Use './run_server_background.sh status' to check status"
}

stop_server() {
    echo "🛑 Stopping NoCoDB MCP Server..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ No PID file found. Server may not be running."
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        echo "✅ Server stopped successfully (PID: $PID)"
    else
        echo "❌ Server not running (stale PID file removed)"
        rm -f "$PID_FILE"
    fi
}

status_server() {
    echo "📊 NoCoDB MCP Server Status:"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ Server is running (PID: $PID)"
            echo "   Log file: $LOG_FILE"
            if [ -f "$LOG_FILE" ]; then
                echo "   Last 5 log lines:"
                tail -5 "$LOG_FILE" | sed 's/^/      /'
            fi
        else
            echo "❌ Server not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ Server is not running"
    fi
}

show_logs() {
    echo "📋 NoCoDB MCP Server Logs:"
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found"
    fi
}

case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        status_server
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the MCP server in background"
        echo "  stop     - Stop the background MCP server"
        echo "  restart  - Restart the MCP server"
        echo "  status   - Check if server is running"
        echo "  logs     - Show server logs (follow mode)"
        echo ""
        echo "Default: start"
        exit 1
        ;;
esac
