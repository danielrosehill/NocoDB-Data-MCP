# Windsurf MCP Configuration

## Adding NoCoDB MCP Server to Windsurf

To use the NoCoDB MCP server with Windsurf, add this configuration to your Windsurf settings:

### Configuration JSON

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

### How to Add This Configuration

1. **Open Windsurf Settings**
   - Press `Ctrl+,` or go to File → Preferences → Settings

2. **Find MCP Settings**
   - Search for "MCP" in the settings search bar
   - Look for "MCP Servers" configuration

3. **Add the Configuration**
   - Paste the JSON configuration above
   - Save the settings

4. **Restart Windsurf**
   - Close and reopen Windsurf to load the new MCP server

### Verification

After adding the configuration, you should be able to use commands like:

- "List all my NoCoDB bases"
- "Show me tables in the Personal base"
- "Create a new record in the Tasks table"

### Troubleshooting

If the MCP server doesn't load:

1. **Check the path**: Ensure the path `/home/daniel/repos/github/NocoDB-Control-MCP-Local/venv/bin/python` exists
2. **Test manually**: Run `python test_connection.py` from the project directory
3. **Check logs**: Look at Windsurf's developer console for MCP-related errors

### Alternative Configuration (if using different Python)

If you prefer to use your system Python with uv or a different virtual environment:

```json
{
  "mcpServers": {
    "nocodb": {
      "command": "python3",
      "args": ["-m", "nocodb_mcp.server"],
      "cwd": "/home/daniel/repos/github/NocoDB-Control-MCP-Local",
      "env": {
        "PYTHONPATH": "/home/daniel/repos/github/NocoDB-Control-MCP-Local/src"
      }
    }
  }
}
```

## Available Tools After Setup

Once configured, you'll have access to these NoCoDB operations through natural language:

- **Base Management**: List, create, get info about bases
- **Table Operations**: List tables, get schema, copy tables between bases  
- **Data CRUD**: Create, read, update, delete records
- **Pagination**: Get data with limits and offsets

Your NoCoDB instance at `db.dsrholdingsai.com` with 17 bases will be fully accessible through Windsurf!
