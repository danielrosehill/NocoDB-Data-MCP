#!/usr/bin/env python3
"""
Test script to verify NoCoDB MCP server connection and configuration.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nocodb_mcp.server import load_config, NocoDBClient

async def test_connection():
    """Test connection to NoCoDB instance."""
    print("Testing NoCoDB MCP Server connection...")
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print(f"Host: {config['host']}")
        print(f"API Token: {'*' * (len(config['api_token']) - 4) + config['api_token'][-4:]}")
        print(f"CF Client ID: {config['cf_client_id'][:20]}...")
        
        # Initialize client
        client = NocoDBClient(
            base_url=config['host'],
            api_token=config['api_token'],
            cf_client_id=config['cf_client_id'],
            cf_client_secret=config['cf_client_secret']
        )
        
        # Test connection by listing bases
        print("\nTesting API connection...")
        bases = await client.list_bases()
        
        print(f"✅ Connection successful!")
        print(f"Found {len(bases)} bases:")
        
        for base in bases[:5]:  # Show first 5 bases
            print(f"  - {base.get('title', 'Unnamed')} (ID: {base.get('id', 'N/A')})")
        
        if len(bases) > 5:
            print(f"  ... and {len(bases) - 5} more")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
