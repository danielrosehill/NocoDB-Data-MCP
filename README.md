# NoCoDB Data MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: Custom](https://img.shields.io/badge/License-Custom-yellow.svg)](LICENSE)
[![NoCoDB](https://img.shields.io/badge/NoCoDB-Ready-orange.svg)](https://nocodb.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Model Context Protocol (MCP) server that provides a natural language interface for NoCoDB operations. This server runs locally and connects to your NoCoDB instance via authenticated API calls, supporting Cloudflare Access protection.

> 🚀 **Transform your NoCoDB database into an AI-powered assistant!** Use natural language to query, create, update, and manage your NoCoDB data through any MCP-compatible AI client like Windsurf, Claude Desktop, or other MCP-enabled tools.

## 🎯 What This Does

This MCP server acts as a bridge between AI assistants and your NoCoDB database, enabling you to:
- **Query data** using natural language ("Show me all customers from last month")
- **Create records** through conversation ("Add a new project with these details...")
- **Manage database structure** ("Create a new table for tracking expenses")
- **Automate workflows** ("Update all pending tasks to completed status")

All while maintaining security through local execution and proper authentication.

## ✨ Features

### Core Capabilities
- 🏠 **Local MCP Server**: Runs on your local machine, no remote deployment needed
- 🗣️ **Natural Language Interface**: Use AI assistants to perform NoCoDB operations with natural language
- 🔐 **Cloudflare Access Support**: Handles authentication through Cloudflare Access headers
- ⚡ **Fast & Lightweight**: Minimal dependencies, quick setup
- 🔒 **Secure**: All credentials stored locally, no data sent to third parties

### Database Operations
- 📊 **Complete CRUD Operations**: Create, read, update, and delete records
- 🗂️ **Base Management**: List, create, and manage NoCoDB bases (projects)
- 🔧 **Table Operations**: Create, list, duplicate, and delete tables
- 📋 **Schema Management**: Add, update, and remove columns
- 👁️ **View Management**: Create and manage custom views with filters and sorting
- 🔗 **Webhook Integration**: Set up and test webhooks for real-time notifications
- 🔍 **Advanced Querying**: Filter, sort, and paginate through large datasets

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A NoCoDB instance (cloud or self-hosted)
- An MCP-compatible AI client:
  - [Windsurf](https://codeium.com/windsurf) (recommended)
  - [Claude Desktop](https://claude.ai/desktop)
  - Any other MCP-compatible client
- NoCoDB API token (see [Configuration](#️-configuration))

## 📦 Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/danielrosehill/NocoDB-Data-MCP.git
   cd NocoDB-Data-MCP
   ```

2. **Run the installation script**:
   ```bash
   ./install.sh
   ```
   
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Install the MCP server in development mode

3. **Configure your NoCoDB connection** (see [Configuration](#️-configuration) section below)

4. **Verify installation**:
   ```bash
   source venv/bin/activate
   python testing/test_connection.py
   ```

## ⚙️ Configuration

Before running the server, you need to configure your NoCoDB connection:

1. **Copy the example configuration files:**
   ```bash
   cp cloudflare-examples/cf.json.example cf.json
   cp json-examples/nocodb.json.example nocodb.json
   ```

2. **Edit the configuration files:**
   - `nocodb.json`: Replace `YOUR_NOCODB_API_TOKEN_HERE` with your actual NoCoDB API token and update the base URL
   - `cf.json`: Configure Cloudflare Access credentials (only if using Cloudflare Access)

3. **See [CONFIGURATION.md](CONFIGURATION.md) for detailed setup instructions**

⚠️ **Security Note:** The actual configuration files (`nocodb.json`, `cf.json`) are ignored by git to prevent accidental exposure of sensitive credentials.

### 🔐 Cloudflare Access Setup

If your NoCoDB instance is protected by Cloudflare Access, you'll need to configure service token authentication:

1. **Create a Service Token:**
   - Go to your Cloudflare dashboard → Zero Trust → Access → Service Tokens
   - Click "Create Service Token"
   - Give it a descriptive name (e.g., "NoCoDB MCP Server")
   - Copy the Client ID and Client Secret

2. **Create an Access Policy:**
   - Go to Zero Trust → Access → Applications
   - Find your NoCoDB application
   - Edit the application and go to "Policies"
   - Create a new policy with:
     - **Action:** Bypass
     - **Rule:** Service Token
     - **Value:** Select your created service token

3. **Configure the MCP Server:**
   - Add the Client ID and Secret to your `cf.json` file
   - The server will automatically include the required headers in all requests

**Why Cloudflare Access?** This setup allows you to keep your NoCoDB instance secure behind Cloudflare's authentication while still enabling programmatic access through the MCP server. The service token acts as a "machine user" that can bypass the normal login flow.

## 🎯 Usage

### Running the MCP Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python -m nocodb_mcp.server
```

### Using with AI Assistants

#### Windsurf Configuration

Add this server to your Windsurf MCP configuration (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "nocodb-data": {
      "command": "/path/to/NocoDB-Data-MCP/venv/bin/python",
      "args": ["-m", "nocodb_mcp.server"],
      "cwd": "/path/to/NocoDB-Data-MCP"
    }
  }
}
```

#### General MCP Client Configuration

For other MCP clients, use this format:

```json
{
  "mcpServers": {
    "nocodb": {
      "command": "/path/to/NocoDB-Data-MCP/venv/bin/python",
      "args": ["-m", "nocodb_mcp.server"],
      "cwd": "/path/to/NocoDB-Data-MCP"
    }
  }
}
```

### 🛠️ Available Tools

The MCP server provides 30 comprehensive tools for NoCoDB operations:

#### Base & Project Management
- `list_bases`: List all bases (projects) in your NoCoDB instance
- `get_base_info`: Get detailed information about a specific base
- `create_base`: Create a new base/project

#### Table Operations
- `list_tables`: List all tables in a base
- `get_table_info`: Get detailed table schema and metadata
- `create_table`: Create a new table with custom columns
- `duplicate_table`: Duplicate an existing table with options
- `delete_table`: Remove a table from the base

#### Column Management
- `create_column`: Add new columns to existing tables
- `update_column`: Modify column properties and constraints
- `delete_column`: Remove columns from tables

#### Data Operations (CRUD)
- `get_table_data`: Retrieve records with pagination and filtering
- `get_record`: Get a specific record by ID
- `create_record`: Insert new records into tables
- `update_record`: Modify existing records
- `delete_record`: Remove records from tables
- `bulk_insert_records`: Insert multiple records at once
- `bulk_update_records`: Update multiple records simultaneously
- `bulk_delete_records`: Delete multiple records in one operation
- `get_table_count`: Get record count with optional filtering
- `export_table_data`: Export data in CSV, Excel, or JSON formats
- `get_table_schema`: Get complete table schema and metadata

#### Views & Filtering
- `create_view`: Create custom views (Grid, Gallery, Form, etc.)
- `list_views`: List all views for a table
- `delete_view`: Remove views
- `create_filter`: Add filters to views
- `list_filters`: List all filters for a view
- `delete_filter`: Remove filters

#### Sorting & Organization
- `create_sort`: Add sorting rules to views
- `list_sorts`: List all sorting rules for a view
- `delete_sort`: Remove sorting rules

#### Webhook Integration
- `create_webhook`: Set up webhooks for real-time notifications
- `list_webhooks`: List all webhooks for a table
- `delete_webhook`: Remove webhooks
- `test_webhook`: Test webhook configurations

### 💬 Example Natural Language Commands

Once connected to an AI assistant with MCP support, you can use commands like:

- "List all my NoCoDB bases"
- "Show me the tables in the 'CRM' base"
- "Copy the 'Customers' table to a new base called 'Archive'"
- "Create a new record in the 'Tasks' table with title 'Review docs' and status 'Todo'"
- "Show me the first 10 records from the 'Orders' table"

## 🏗️ Architecture

```
Local Machine                    Remote NoCoDB
┌─────────────────┐             ┌──────────────────┐
│   AI Assistant  │             │                  │
│        │        │             │   your-nocodb    │
│        ▼        │   HTTPS     │   instance.com   │
│   MCP Client    │◄───────────►│                  │
│        │        │   API Calls │   (Behind        │
│        ▼        │             │   Cloudflare     │
│ NoCoDB MCP      │             │   Access)        │
│ Server (Local)  │             │                  │
└─────────────────┘             └──────────────────┘
```

The MCP server acts as a local client that:
1. Receives tool calls from AI assistants
2. Translates them into NoCoDB API calls
3. Handles Cloudflare Access authentication
4. Returns structured responses

## 🔧 Development

To contribute or modify the server:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is shared in the best of faith for the benefit of the community. Development was primarily accomplished by Claude 3.5 Sonnet (Anthropic's AI assistant) working collaboratively with Daniel Rosehill. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NoCoDB](https://nocodb.com/) for providing an excellent no-code database platform
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- The open-source community for inspiration and support

## 📞 Support

If you encounter any issues or have questions:

1. Check the [CONFIGURATION.md](CONFIGURATION.md) for detailed setup instructions
2. Look through existing [Issues](https://github.com/danielrosehill/NocoDB-Data-MCP/issues)
3. Create a new issue if your problem isn't already covered

## 🗺️ Roadmap

- [ ] Support for environment variable configuration
- [ ] Docker containerization
- [ ] Additional authentication methods
- [ ] Webhook support for real-time updates
- [ ] Enhanced error handling and logging
- [ ] Performance optimizations for large datasets

---

**Made with ❤️ for the NoCoDB and MCP communities**
