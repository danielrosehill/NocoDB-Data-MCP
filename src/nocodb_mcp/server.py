#!/usr/bin/env python3
"""
NoCoDB MCP Server

A Model Context Protocol server that runs locally and provides tools for 
interacting with remote NoCoDB instances through natural language commands.
Supports CRUD operations, table management, and base operations.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nocodb-mcp")

class NocoDBClient:
    """Client for interacting with remote NoCoDB API through Cloudflare Access."""
    
    def __init__(self, base_url: str, api_token: str, cf_client_id: str, cf_client_secret: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.cf_client_id = cf_client_id
        self.cf_client_secret = cf_client_secret
        
        # Default headers for all requests
        self.headers = {
            'xc-token': self.api_token,
            'Content-Type': 'application/json',
            'CF-Access-Client-Id': self.cf_client_id,
            'CF-Access-Client-Secret': self.cf_client_secret
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to NoCoDB API."""
        url = f"{self.base_url}/api/v2{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                raise Exception(f"API request failed: {str(e)}")
            except Exception as e:
                logger.error(f"Request error: {e}")
                raise Exception(f"Request failed: {str(e)}")
    
    async def list_bases(self) -> List[Dict[str, Any]]:
        """List all bases (projects) in NoCoDB."""
        result = await self._make_request('GET', '/meta/bases')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def get_base_info(self, base_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific base."""
        return await self._make_request('GET', f'/meta/bases/{base_id}/info')
    
    async def list_tables(self, base_id: str) -> List[Dict[str, Any]]:
        """List all tables in a base."""
        result = await self._make_request('GET', f'/meta/bases/{base_id}/tables')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        return await self._make_request('GET', f'/meta/tables/{table_id}')
    
    async def create_base(self, title: str, description: str = "") -> Dict[str, Any]:
        """Create a new base."""
        data = {
            'title': title,
            'description': description
        }
        return await self._make_request('POST', '/meta/bases', data)
    
    async def create_table(self, base_id: str, title: str, table_name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new table in a base."""
        data = {
            'table_name': table_name,
            'title': title,
            'columns': columns
        }
        return await self._make_request('POST', f'/meta/bases/{base_id}/tables', data)
    
    async def create_column(self, table_id: str, column_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new column in a table."""
        return await self._make_request('POST', f'/meta/tables/{table_id}/columns', column_data)
    
    async def update_column(self, table_id: str, column_id: str, column_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing column."""
        return await self._make_request('PATCH', f'/meta/tables/{table_id}/columns/{column_id}', column_data)
    
    async def delete_column(self, table_id: str, column_id: str) -> Dict[str, Any]:
        """Delete a column from a table."""
        return await self._make_request('DELETE', f'/meta/tables/{table_id}/columns/{column_id}')
    
    async def duplicate_table(self, table_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Duplicate a table with specified options."""
        return await self._make_request('POST', f'/meta/tables/{table_id}/duplicate', options)
    
    async def delete_table(self, table_id: str) -> Dict[str, Any]:
        """Delete a table."""
        return await self._make_request('DELETE', f'/meta/tables/{table_id}')
    
    async def create_view(self, table_id: str, view_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new view for a table."""
        view_type = view_data.get('type', 'grid')
        if view_type == 'grid':
            return await self._make_request('POST', f'/meta/tables/{table_id}/grids', view_data)
        elif view_type == 'form':
            return await self._make_request('POST', f'/meta/tables/{table_id}/forms', view_data)
        elif view_type == 'gallery':
            return await self._make_request('POST', f'/meta/tables/{table_id}/galleries', view_data)
        elif view_type == 'kanban':
            return await self._make_request('POST', f'/meta/tables/{table_id}/kanbans', view_data)
        else:
            raise ValueError(f"Unsupported view type: {view_type}")
    
    async def list_views(self, table_id: str) -> List[Dict[str, Any]]:
        """List all views for a table."""
        result = await self._make_request('GET', f'/meta/tables/{table_id}/views')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def delete_view(self, view_id: str) -> Dict[str, Any]:
        """Delete a view."""
        return await self._make_request('DELETE', f'/meta/views/{view_id}')
    
    async def create_filter(self, view_id: str, filter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a filter for a view."""
        return await self._make_request('POST', f'/meta/views/{view_id}/filters', filter_data)
    
    async def list_filters(self, view_id: str) -> List[Dict[str, Any]]:
        """List all filters for a view."""
        result = await self._make_request('GET', f'/meta/views/{view_id}/filters')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def delete_filter(self, filter_id: str) -> Dict[str, Any]:
        """Delete a filter."""
        return await self._make_request('DELETE', f'/meta/filters/{filter_id}')
    
    async def create_sort(self, view_id: str, sort_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sort for a view."""
        return await self._make_request('POST', f'/meta/views/{view_id}/sorts', sort_data)
    
    async def list_sorts(self, view_id: str) -> List[Dict[str, Any]]:
        """List all sorts for a view."""
        result = await self._make_request('GET', f'/meta/views/{view_id}/sorts')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def delete_sort(self, sort_id: str) -> Dict[str, Any]:
        """Delete a sort."""
        return await self._make_request('DELETE', f'/meta/sorts/{sort_id}')
    
    async def create_webhook(self, table_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a webhook for a table."""
        return await self._make_request('POST', f'/meta/tables/{table_id}/hooks', webhook_data)
    
    async def list_webhooks(self, table_id: str) -> List[Dict[str, Any]]:
        """List all webhooks for a table."""
        result = await self._make_request('GET', f'/meta/tables/{table_id}/hooks')
        return result.get('list', []) if isinstance(result, dict) else result
    
    async def delete_webhook(self, hook_id: str) -> Dict[str, Any]:
        """Delete a webhook."""
        return await self._make_request('DELETE', f'/meta/hooks/{hook_id}')
    
    async def test_webhook(self, table_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a webhook configuration."""
        return await self._make_request('POST', f'/meta/tables/{table_id}/hooks/test', webhook_data)
    
    async def get_table_data(self, table_id: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """Get data from a table."""
        endpoint = f'/tables/{table_id}/records?limit={limit}&offset={offset}'
        return await self._make_request('GET', endpoint)
    
    async def create_record(self, table_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in a table."""
        return await self._make_request('POST', f'/tables/{table_id}/records', data)
    
    async def update_record(self, table_id: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in a table."""
        return await self._make_request('PATCH', f'/tables/{table_id}/records/{record_id}', data)
    
    async def delete_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        """Delete a record from a table."""
        return await self._make_request('DELETE', f'/tables/{table_id}/records/{record_id}')
    
    async def get_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        """Get a specific record from a table."""
        return await self._make_request('GET', f'/tables/{table_id}/records/{record_id}')
    
    async def bulk_insert_records(self, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk insert multiple records into a table."""
        return await self._make_request('POST', f'/tables/{table_id}/records', records)
    
    async def bulk_update_records(self, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk update multiple records in a table."""
        return await self._make_request('PATCH', f'/tables/{table_id}/records', records)
    
    async def bulk_delete_records(self, table_id: str, record_ids: List[str]) -> Dict[str, Any]:
        """Bulk delete multiple records from a table."""
        data = {'ids': record_ids}
        return await self._make_request('DELETE', f'/tables/{table_id}/records', data)
    
    async def get_table_schema(self, table_id: str) -> Dict[str, Any]:
        """Get the complete schema information for a table including columns, relations, etc."""
        return await self._make_request('GET', f'/meta/tables/{table_id}')
    
    async def export_table_data(self, table_id: str, export_type: str = 'csv') -> Dict[str, Any]:
        """Export table data in various formats (csv, excel, json)."""
        return await self._make_request('GET', f'/tables/{table_id}/export/{export_type}')
    
    async def get_table_count(self, table_id: str, where: Optional[str] = None) -> Dict[str, Any]:
        """Get the count of records in a table with optional filtering."""
        params = {'count': 'true'}
        if where:
            params['where'] = where
        endpoint = f'/tables/{table_id}/count'
        if params:
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            endpoint += f'?{query_string}'
        return await self._make_request('GET', endpoint)

# Initialize the MCP server
server = Server("nocodb-mcp")

# Load configuration from JSON files
def load_config():
    """Load configuration from JSON files."""
    config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Load NoCoDB config
    nocodb_config_path = os.path.join(config_dir, 'nocodb.json')
    with open(nocodb_config_path, 'r') as f:
        nocodb_config = json.load(f)
    
    # Load Cloudflare config
    cf_config_path = os.path.join(config_dir, 'cf.json')
    with open(cf_config_path, 'r') as f:
        cf_config = json.load(f)
    
    # Load target host
    host_file_path = os.path.join(config_dir, 'thetask.m d')
    with open(host_file_path, 'r') as f:
        host = f.read().strip()
    
    # Extract credentials
    api_token = None
    for field in nocodb_config['details']['sections'][0]['fields']:
        if field['t'] == 'credential':
            api_token = field['v']
            break
    
    cf_client_id = None
    cf_client_secret = None
    for field in cf_config['details']['sections'][0]['fields']:
        if 'CF-Access-Client-Id' in field['v']:
            cf_client_id = field['v'].split(': ')[1]
        elif 'CF-Access-Client-Secret' in field['v']:
            cf_client_secret = field['v'].split(': ')[1]
    
    return {
        'host': f"https://{host}",
        'api_token': api_token,
        'cf_client_id': cf_client_id,
        'cf_client_secret': cf_client_secret
    }

# Initialize client
config = load_config()
nocodb_client = NocoDBClient(
    base_url=config['host'],
    api_token=config['api_token'],
    cf_client_id=config['cf_client_id'],
    cf_client_secret=config['cf_client_secret']
)

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available NoCoDB tools."""
    return [
        Tool(
            name="list_bases",
            description="List all bases (projects) in NoCoDB",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_base_info",
            description="Get detailed information about a specific base",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_id": {
                        "type": "string",
                        "description": "The ID of the base to get information about"
                    }
                },
                "required": ["base_id"]
            }
        ),
        Tool(
            name="create_base",
            description="Create a new base (project) in NoCoDB",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the new base"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the base"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in a base",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_id": {
                        "type": "string",
                        "description": "The ID of the base to list tables from"
                    }
                },
                "required": ["base_id"]
            }
        ),
        Tool(
            name="get_table_info",
            description="Get detailed information about a table including columns and schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to get information about"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="create_table",
            description="Create a new table in a base with specified columns",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_id": {
                        "type": "string",
                        "description": "The ID of the base to create the table in"
                    },
                    "title": {
                        "type": "string",
                        "description": "The display title of the table"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "The internal name of the table"
                    },
                    "columns": {
                        "type": "array",
                        "description": "Array of column definitions",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column_name": {"type": "string"},
                                "title": {"type": "string"},
                                "uidt": {"type": "string", "description": "Column type (SingleLineText, LongText, Number, etc.)"},
                                "dt": {"type": "string", "description": "Database type"},
                                "np": {"type": "string", "description": "Numeric precision"},
                                "ns": {"type": "string", "description": "Numeric scale"}
                            }
                        }
                    }
                },
                "required": ["base_id", "title", "table_name", "columns"]
            }
        ),
        Tool(
            name="delete_table",
            description="Delete a table from a base",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to delete"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="create_column",
            description="Create a new column in an existing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to add the column to"
                    },
                    "column_data": {
                        "type": "object",
                        "description": "Column definition including name, type, and properties",
                        "properties": {
                            "column_name": {"type": "string"},
                            "title": {"type": "string"},
                            "uidt": {"type": "string", "description": "Column type (SingleLineText, LongText, Number, etc.)"},
                            "dt": {"type": "string", "description": "Database type"},
                            "rqd": {"type": "boolean", "description": "Required field"}
                        }
                    }
                },
                "required": ["table_id", "column_data"]
            }
        ),
        Tool(
            name="update_column",
            description="Update an existing column in a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table containing the column"
                    },
                    "column_id": {
                        "type": "string",
                        "description": "The ID of the column to update"
                    },
                    "column_data": {
                        "type": "object",
                        "description": "Updated column properties"
                    }
                },
                "required": ["table_id", "column_id", "column_data"]
            }
        ),
        Tool(
            name="delete_column",
            description="Delete a column from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table containing the column"
                    },
                    "column_id": {
                        "type": "string",
                        "description": "The ID of the column to delete"
                    }
                },
                "required": ["table_id", "column_id"]
            }
        ),
        Tool(
            name="create_view",
            description="Create a new view for a table (grid, form, gallery, kanban)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to create the view for"
                    },
                    "view_data": {
                        "type": "object",
                        "description": "View configuration",
                        "properties": {
                            "title": {"type": "string", "description": "View title"},
                            "type": {"type": "string", "enum": ["grid", "form", "gallery", "kanban"], "description": "View type"}
                        }
                    }
                },
                "required": ["table_id", "view_data"]
            }
        ),
        Tool(
            name="list_views",
            description="List all views for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to list views for"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="delete_view",
            description="Delete a view",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {
                        "type": "string",
                        "description": "The ID of the view to delete"
                    }
                },
                "required": ["view_id"]
            }
        ),
        Tool(
            name="create_filter",
            description="Create a filter for a view",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {
                        "type": "string",
                        "description": "The ID of the view to create the filter for"
                    },
                    "filter_data": {
                        "type": "object",
                        "description": "Filter configuration",
                        "properties": {
                            "fk_column_id": {"type": "string", "description": "Column ID to filter on"},
                            "comparison_op": {"type": "string", "description": "Comparison operator (eq, neq, like, etc.)"},
                            "value": {"type": "string", "description": "Filter value"}
                        }
                    }
                },
                "required": ["view_id", "filter_data"]
            }
        ),
        Tool(
            name="list_filters",
            description="List all filters for a view",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {
                        "type": "string",
                        "description": "The ID of the view to list filters for"
                    }
                },
                "required": ["view_id"]
            }
        ),
        Tool(
            name="delete_filter",
            description="Delete a filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_id": {
                        "type": "string",
                        "description": "The ID of the filter to delete"
                    }
                },
                "required": ["filter_id"]
            }
        ),
        Tool(
            name="create_sort",
            description="Create a sort for a view",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {
                        "type": "string",
                        "description": "The ID of the view to create the sort for"
                    },
                    "sort_data": {
                        "type": "object",
                        "description": "Sort configuration",
                        "properties": {
                            "fk_column_id": {"type": "string", "description": "Column ID to sort by"},
                            "direction": {"type": "string", "enum": ["asc", "desc"], "description": "Sort direction"}
                        }
                    }
                },
                "required": ["view_id", "sort_data"]
            }
        ),
        Tool(
            name="list_sorts",
            description="List all sorts for a view",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {
                        "type": "string",
                        "description": "The ID of the view to list sorts for"
                    }
                },
                "required": ["view_id"]
            }
        ),
        Tool(
            name="delete_sort",
            description="Delete a sort",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort_id": {
                        "type": "string",
                        "description": "The ID of the sort to delete"
                    }
                },
                "required": ["sort_id"]
            }
        ),
        Tool(
            name="create_webhook",
            description="Create a webhook for table events",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to create the webhook for"
                    },
                    "webhook_data": {
                        "type": "object",
                        "description": "Webhook configuration",
                        "properties": {
                            "title": {"type": "string", "description": "Webhook title"},
                            "notification": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["URL", "Email", "Slack", "Discord", "Teams"]},
                                    "payload": {"type": "object"}
                                }
                            },
                            "event": {"type": "string", "enum": ["after", "before"], "description": "When to trigger"},
                            "operation": {"type": "string", "enum": ["insert", "update", "delete"], "description": "Which operation to watch"}
                        }
                    }
                },
                "required": ["table_id", "webhook_data"]
            }
        ),
        Tool(
            name="list_webhooks",
            description="List all webhooks for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to list webhooks for"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="delete_webhook",
            description="Delete a webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "hook_id": {
                        "type": "string",
                        "description": "The ID of the webhook to delete"
                    }
                },
                "required": ["hook_id"]
            }
        ),
        Tool(
            name="test_webhook",
            description="Test a webhook configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to test the webhook for"
                    },
                    "webhook_data": {
                        "type": "object",
                        "description": "Webhook configuration to test"
                    }
                },
                "required": ["table_id", "webhook_data"]
            }
        ),
        Tool(
            name="duplicate_table",
            description="Duplicate a table within the same base (copy_table_to_base alternative)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to duplicate"
                    },
                    "options": {
                        "type": "object",
                        "description": "Duplication options",
                        "properties": {
                            "includeData": {"type": "boolean", "description": "Include table data"},
                            "excludeHooks": {"type": "boolean", "description": "Exclude webhooks"},
                            "excludeViews": {"type": "boolean", "description": "Exclude views"}
                        }
                    }
                },
                "required": ["table_id", "options"]
            }
        ),
        Tool(
            name="get_table_data",
            description="Get data from a table with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to get data from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of records to return (default: 25)"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of records to skip (default: 0)"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="create_record",
            description="Create a new record in a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table to create a record in"
                    },
                    "data": {
                        "type": "object",
                        "description": "The data for the new record as key-value pairs"
                    }
                },
                "required": ["table_id", "data"]
            }
        ),
        Tool(
            name="update_record",
            description="Update an existing record in a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table containing the record"
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The ID of the record to update"
                    },
                    "data": {
                        "type": "object",
                        "description": "The updated data as key-value pairs"
                    }
                },
                "required": ["table_id", "record_id", "data"]
            }
        ),
        Tool(
            name="delete_record",
            description="Delete a record from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table containing the record"
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The ID of the record to delete"
                    }
                },
                "required": ["table_id", "record_id"]
            }
        ),
        Tool(
            name="get_record",
            description="Get a specific record from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "record_id": {
                        "type": "string",
                        "description": "The ID of the record to retrieve"
                    }
                },
                "required": ["table_id", "record_id"]
            }
        ),
        Tool(
            name="bulk_insert_records",
            description="Bulk insert multiple records into a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "records": {
                        "type": "array",
                        "description": "Array of record objects to insert",
                        "items": {
                            "type": "object"
                        }
                    }
                },
                "required": ["table_id", "records"]
            }
        ),
        Tool(
            name="bulk_update_records",
            description="Bulk update multiple records in a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "records": {
                        "type": "array",
                        "description": "Array of record objects to update (must include record IDs)",
                        "items": {
                            "type": "object"
                        }
                    }
                },
                "required": ["table_id", "records"]
            }
        ),
        Tool(
            name="bulk_delete_records",
            description="Bulk delete multiple records from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "record_ids": {
                        "type": "array",
                        "description": "Array of record IDs to delete",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["table_id", "record_ids"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get complete schema information for a table including columns, relations, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="export_table_data",
            description="Export table data in various formats (csv, excel, json)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "export_type": {
                        "type": "string",
                        "description": "Export format: csv, excel, or json",
                        "enum": ["csv", "excel", "json"],
                        "default": "csv"
                    }
                },
                "required": ["table_id"]
            }
        ),
        Tool(
            name="get_table_count",
            description="Get the count of records in a table with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The ID of the table"
                    },
                    "where": {
                        "type": "string",
                        "description": "Optional WHERE clause for filtering records"
                    }
                },
                "required": ["table_id"]
            }
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for NoCoDB operations."""
    try:
        if name == "list_bases":
            result = await nocodb_client.list_bases()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_base_info":
            base_id = arguments.get("base_id")
            if not base_id:
                raise ValueError("base_id is required")
            result = await nocodb_client.get_base_info(base_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_tables":
            base_id = arguments.get("base_id")
            if not base_id:
                raise ValueError("base_id is required")
            result = await nocodb_client.list_tables(base_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_table_info":
            table_id = arguments.get("table_id")
            if not table_id:
                raise ValueError("table_id is required")
            result = await nocodb_client.get_table_info(table_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_base":
            title = arguments.get("title")
            description = arguments.get("description", "")
            if not title:
                raise ValueError("title is required")
            result = await nocodb_client.create_base(title, description)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_table":
            base_id = arguments.get("base_id")
            title = arguments.get("title")
            table_name = arguments.get("table_name")
            columns = arguments.get("columns")
            
            if not all([base_id, title, table_name, columns]):
                raise ValueError("base_id, title, table_name, and columns are required")
            
            result = await nocodb_client.create_table(base_id, title, table_name, columns)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_table":
            table_id = arguments.get("table_id")
            if not table_id:
                raise ValueError("table_id is required")
            result = await nocodb_client.delete_table(table_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_column":
            table_id = arguments.get("table_id")
            column_data = arguments.get("column_data")
            
            if not all([table_id, column_data]):
                raise ValueError("table_id and column_data are required")
            
            result = await nocodb_client.create_column(table_id, column_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "update_column":
            table_id = arguments.get("table_id")
            column_id = arguments.get("column_id")
            column_data = arguments.get("column_data")
            
            if not all([table_id, column_id, column_data]):
                raise ValueError("table_id, column_id, and column_data are required")
            
            result = await nocodb_client.update_column(table_id, column_id, column_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_column":
            table_id = arguments.get("table_id")
            column_id = arguments.get("column_id")
            
            if not all([table_id, column_id]):
                raise ValueError("table_id and column_id are required")
            
            result = await nocodb_client.delete_column(table_id, column_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_view":
            table_id = arguments.get("table_id")
            view_data = arguments.get("view_data")
            
            if not all([table_id, view_data]):
                raise ValueError("table_id and view_data are required")
            
            result = await nocodb_client.create_view(table_id, view_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_views":
            table_id = arguments.get("table_id")
            if not table_id:
                raise ValueError("table_id is required")
            result = await nocodb_client.list_views(table_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_view":
            view_id = arguments.get("view_id")
            if not view_id:
                raise ValueError("view_id is required")
            result = await nocodb_client.delete_view(view_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_filter":
            view_id = arguments.get("view_id")
            filter_data = arguments.get("filter_data")
            
            if not all([view_id, filter_data]):
                raise ValueError("view_id and filter_data are required")
            
            result = await nocodb_client.create_filter(view_id, filter_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_filters":
            view_id = arguments.get("view_id")
            if not view_id:
                raise ValueError("view_id is required")
            result = await nocodb_client.list_filters(view_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_filter":
            filter_id = arguments.get("filter_id")
            if not filter_id:
                raise ValueError("filter_id is required")
            result = await nocodb_client.delete_filter(filter_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_sort":
            view_id = arguments.get("view_id")
            sort_data = arguments.get("sort_data")
            
            if not all([view_id, sort_data]):
                raise ValueError("view_id and sort_data are required")
            
            result = await nocodb_client.create_sort(view_id, sort_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_sorts":
            view_id = arguments.get("view_id")
            if not view_id:
                raise ValueError("view_id is required")
            result = await nocodb_client.list_sorts(view_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_sort":
            sort_id = arguments.get("sort_id")
            if not sort_id:
                raise ValueError("sort_id is required")
            result = await nocodb_client.delete_sort(sort_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_webhook":
            table_id = arguments.get("table_id")
            webhook_data = arguments.get("webhook_data")
            
            if not all([table_id, webhook_data]):
                raise ValueError("table_id and webhook_data are required")
            
            result = await nocodb_client.create_webhook(table_id, webhook_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_webhooks":
            table_id = arguments.get("table_id")
            if not table_id:
                raise ValueError("table_id is required")
            result = await nocodb_client.list_webhooks(table_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_webhook":
            hook_id = arguments.get("hook_id")
            if not hook_id:
                raise ValueError("hook_id is required")
            result = await nocodb_client.delete_webhook(hook_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "test_webhook":
            table_id = arguments.get("table_id")
            webhook_data = arguments.get("webhook_data")
            
            if not all([table_id, webhook_data]):
                raise ValueError("table_id and webhook_data are required")
            
            result = await nocodb_client.test_webhook(table_id, webhook_data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "duplicate_table":
            table_id = arguments.get("table_id")
            options = arguments.get("options")
            
            if not all([table_id, options]):
                raise ValueError("table_id and options are required")
            
            result = await nocodb_client.duplicate_table(table_id, options)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_table_data":
            table_id = arguments.get("table_id")
            limit = arguments.get("limit", 25)
            offset = arguments.get("offset", 0)
            
            if not table_id:
                raise ValueError("table_id is required")
            
            result = await nocodb_client.get_table_data(table_id, limit, offset)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_record":
            table_id = arguments.get("table_id")
            data = arguments.get("data")
            
            if not table_id or not data:
                raise ValueError("table_id and data are required")
            
            result = await nocodb_client.create_record(table_id, data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "update_record":
            table_id = arguments.get("table_id")
            record_id = arguments.get("record_id")
            data = arguments.get("data")
            
            if not all([table_id, record_id, data]):
                raise ValueError("table_id, record_id, and data are required")
            
            result = await nocodb_client.update_record(table_id, record_id, data)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "delete_record":
            table_id = arguments.get("table_id")
            record_id = arguments.get("record_id")
            
            if not all([table_id, record_id]):
                raise ValueError("table_id and record_id are required")
            
            result = await nocodb_client.delete_record(table_id, record_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_record":
            table_id = arguments.get("table_id")
            record_id = arguments.get("record_id")
            
            if not all([table_id, record_id]):
                raise ValueError("table_id and record_id are required")
            
            result = await nocodb_client.get_record(table_id, record_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "bulk_insert_records":
            table_id = arguments.get("table_id")
            records = arguments.get("records")
            
            if not table_id or not records:
                raise ValueError("table_id and records are required")
            
            result = await nocodb_client.bulk_insert_records(table_id, records)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "bulk_update_records":
            table_id = arguments.get("table_id")
            records = arguments.get("records")
            
            if not table_id or not records:
                raise ValueError("table_id and records are required")
            
            result = await nocodb_client.bulk_update_records(table_id, records)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "bulk_delete_records":
            table_id = arguments.get("table_id")
            record_ids = arguments.get("record_ids")
            
            if not table_id or not record_ids:
                raise ValueError("table_id and record_ids are required")
            
            result = await nocodb_client.bulk_delete_records(table_id, record_ids)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_table_schema":
            table_id = arguments.get("table_id")
            
            if not table_id:
                raise ValueError("table_id is required")
            
            result = await nocodb_client.get_table_schema(table_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "export_table_data":
            table_id = arguments.get("table_id")
            export_type = arguments.get("export_type", "csv")
            
            if not table_id:
                raise ValueError("table_id is required")
            
            result = await nocodb_client.export_table_data(table_id, export_type)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_table_count":
            table_id = arguments.get("table_id")
            where = arguments.get("where")
            
            if not table_id:
                raise ValueError("table_id is required")
            
            result = await nocodb_client.get_table_count(table_id, where)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nocodb-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
