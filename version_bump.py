#!/usr/bin/env python3
"""
Version management script for NoCoDB Data MCP Server
Helps maintain consistent versioning across pyproject.toml and server.py
"""

import re
import sys
from pathlib import Path

def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    return match.group(1)

def update_version(new_version):
    """Update version in both pyproject.toml and server.py"""
    # Update pyproject.toml
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    pyproject_path.write_text(content)
    print(f"Updated pyproject.toml to version {new_version}")
    
    # Update server.py
    server_path = Path("src/nocodb_mcp/server.py")
    if server_path.exists():
        content = server_path.read_text()
        content = re.sub(
            r'server_version="[^"]+"',
            f'server_version="{new_version}"',
            content
        )
        server_path.write_text(content)
        print(f"Updated server.py to version {new_version}")
    
    return True

def main():
    if len(sys.argv) != 2:
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        print("Usage: python version_bump.py <new_version>")
        print("Example: python version_bump.py 1.0.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic semver)
    if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$', new_version):
        print("Error: Version must follow semantic versioning (e.g., 1.0.0, 1.0.0-beta.1)")
        sys.exit(1)
    
    try:
        current_version = get_current_version()
        print(f"Updating version from {current_version} to {new_version}")
        
        if update_version(new_version):
            print(f"✅ Successfully updated version to {new_version}")
            print("\nNext steps:")
            print(f"1. git add .")
            print(f"2. git commit -m 'Bump version to {new_version}'")
            print(f"3. git tag v{new_version}")
            print(f"4. git push origin main --tags")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
