# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-09

### Added
- Initial release of NoCoDB Data MCP Server
- Natural language interface for NoCoDB operations
- Support for all major CRUD operations
- Base and table management capabilities
- Cloudflare Access authentication support
- Local MCP server implementation
- Comprehensive configuration system
- Example configuration files
- Detailed documentation and setup guides

### Features
- `list_bases`: List all bases in your NoCoDB instance
- `get_base_info`: Get detailed information about a specific base
- `list_tables`: List all tables in a base
- `get_table_info`: Get table schema and column information
- `create_base`: Create a new base
- `copy_table_to_base`: Copy a table from one base to another
- `get_table_data`: Retrieve data from a table with pagination
- `create_record`: Create new records in a table
- `update_record`: Update existing records
- `delete_record`: Delete records from a table

### Security
- All sensitive credentials stored locally
- Git ignore patterns for configuration files
- Example templates for safe public sharing
- No data transmission to third parties
