#!/usr/bin/env python3
"""
Test script to verify MCP server tools are working correctly.
This simulates what Windsurf would do when calling MCP tools.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nocodb_mcp.server import handle_call_tool, handle_list_tools

async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("🧪 Testing NoCoDB MCP Server Tools...")
    print("=" * 50)
    
    try:
        # Test 1: List available tools
        print("\n1️⃣ Testing tool listing...")
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test 2: List bases
        print("\n2️⃣ Testing list_bases tool...")
        result = await handle_call_tool("list_bases", {})
        bases_data = json.loads(result[0].text)
        print(f"✅ Found {len(bases_data)} bases:")
        for base in bases_data[:3]:  # Show first 3
            print(f"   - {base.get('title', 'Unnamed')} (ID: {base.get('id', 'N/A')})")
        if len(bases_data) > 3:
            print(f"   ... and {len(bases_data) - 3} more")
        
        # Test 3: Get info about first base
        if bases_data:
            first_base = bases_data[0]
            base_id = first_base.get('id')
            base_title = first_base.get('title', 'Unknown')
            
            print(f"\n3️⃣ Testing get_base_info for '{base_title}'...")
            result = await handle_call_tool("get_base_info", {"base_id": base_id})
            base_info = json.loads(result[0].text)
            print(f"✅ Base info retrieved successfully")
            print(f"   - Title: {base_info.get('title', 'N/A')}")
            print(f"   - Status: {base_info.get('status', 'N/A')}")
            
            # Test 4: List tables in first base
            print(f"\n4️⃣ Testing list_tables for '{base_title}'...")
            result = await handle_call_tool("list_tables", {"base_id": base_id})
            tables_data = json.loads(result[0].text)
            print(f"✅ Found {len(tables_data)} tables:")
            for table in tables_data[:3]:  # Show first 3
                print(f"   - {table.get('title', 'Unnamed')} (ID: {table.get('id', 'N/A')})")
            if len(tables_data) > 3:
                print(f"   ... and {len(tables_data) - 3} more")
        
        print("\n" + "=" * 50)
        print("🎉 All MCP tools are working correctly!")
        print("\nYou can now:")
        print("1. Add the MCP server to Windsurf using the config in docs/windsurf-setup.md")
        print("2. Use natural language commands like:")
        print("   - 'List all my NoCoDB bases'")
        print("   - 'Show me tables in the Personal base'")
        print("   - 'Get the first 10 records from the Tasks table'")
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools())
    sys.exit(0 if success else 1)
