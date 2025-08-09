# NoCoDB MCP Server Usage Guide

## Quick Start

Your NoCoDB MCP server is now installed and ready to use! It successfully connects to your remote NoCoDB instance at `db.dsrholdingsai.com` with 17 bases detected.

## MCP Client Configuration

To use this server with Windsurf or other MCP-compatible AI assistants, add this configuration:

```json
{
  "mcpServers": {
    "nocodb": {
      "command": "/home/daniel/repos/github/NocoDB-Control-MCP-Local/venv/bin/python",
      "args": ["-m", "nocodb_mcp.server"],
      "cwd": "/home/daniel/repos/github/NocoDB-Control-MCP-Local"
    }
  }
}
```

## Available Natural Language Commands

Once connected, you can use natural language commands like:

### Base Management
- "List all my NoCoDB bases"
- "Show me information about the 'Personal' base"
- "Create a new base called 'Project Archive'"

### Table Operations
- "Show me all tables in the 'Household' base"
- "Get the schema for the 'Tasks' table"
- "Copy the 'Customers' table from 'Personal' base to 'Archive' base"

### Data Operations
- "Show me the first 10 records from the 'Medical' table"
- "Create a new record in 'Tasks' with title 'Review MCP server' and status 'In Progress'"
- "Update record ID 123 in 'Personal Finances' table with amount 500"
- "Delete record ID 456 from the 'Automations' table"

## Your Current Bases

The server detected these bases in your NoCoDB instance:
1. **Personal** (ID: pmwrvngu8tw3t9m)
2. **Household** (ID: p62cmte10xj9tfy)
3. **Medical** (ID: p1o4nd4tfqzogk3)
4. **Automations** (ID: pqjbnupor0ds366)
5. **Personal Finances** (ID: pljqctz6w1oemnp)
6. ... and 12 more

## Testing the Server

Run the test script to verify connectivity:
```bash
source venv/bin/activate
python test_connection.py
```

## Running the Server Manually

For debugging or standalone use:
```bash
source venv/bin/activate
python -m nocodb_mcp.server
```

The server will run in stdio mode, waiting for MCP protocol messages.

## Security Notes

- The server runs locally on your machine
- All API calls are made directly to your NoCoDB instance
- Cloudflare Access authentication is handled automatically
- No data is stored locally or transmitted to third parties
