# Testing Guide for NoCoDB MCP Server

## Server Scripts

You now have two scripts to run the MCP server:

### 1. Foreground Mode (stops when terminal closes)
```bash
./run_server.sh
```
- **Use for**: Testing and debugging
- **Behavior**: Runs in terminal, stops when you close terminal or press Ctrl+C
- **Good for**: Seeing real-time logs and MCP protocol messages

### 2. Background Mode (keeps running)
```bash
./run_server_background.sh start    # Start in background
./run_server_background.sh stop     # Stop the server
./run_server_background.sh status   # Check if running
./run_server_background.sh logs     # View logs
./run_server_background.sh restart  # Restart server
```
- **Use for**: Production-like testing with Windsurf
- **Behavior**: Runs as background process, survives terminal closure
- **Good for**: Testing Windsurf integration without keeping terminal open

## Testing with Windsurf

### Step 1: Add MCP Configuration to Windsurf

Add this to your Windsurf MCP settings:
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

### Step 2: Test the Integration

1. **Restart Windsurf** after adding the configuration
2. **Try these natural language commands**:
   - "List all my NoCoDB bases"
   - "Show me tables in the Personal base"
   - "Get information about the Credentials table"
   - "Show me the first 5 records from the Aliexpress Orders table"

### Step 3: Verify It's Working

You should see responses that include data from your NoCoDB instance:
- **17 bases** including Personal, Household, Medical, etc.
- **Tables** like Credentials, Aliexpress Orders, Amazon Orders
- **Actual data** from your tables

## Troubleshooting

### If Windsurf can't connect to MCP server:

1. **Check server is running**:
   ```bash
   ./run_server_background.sh status
   ```

2. **View server logs**:
   ```bash
   ./run_server_background.sh logs
   ```

3. **Test connection manually**:
   ```bash
   python test_connection.py
   ```

4. **Restart the server**:
   ```bash
   ./run_server_background.sh restart
   ```

### If you see authentication errors:

- Check that `nocodb.json` and `cf.json` have correct credentials
- Verify `thetask.m d` has the correct hostname
- Test with: `python test_connection.py`

## Expected Results

When working correctly, you should be able to:

✅ **List bases**: See your 17 NoCoDB bases  
✅ **Browse tables**: View tables in each base  
✅ **Read data**: Get records from tables with pagination  
✅ **Create records**: Add new data to tables  
✅ **Update records**: Modify existing records  
✅ **Delete records**: Remove records from tables  
✅ **Manage bases**: Create new bases and copy tables between them  

All through natural language commands in Windsurf!
