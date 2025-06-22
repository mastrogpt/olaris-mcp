import sys
import json
import os
import platform
import shutil
from pathlib import Path

os.chdir(os.getenv("OPS_PWD") or ".")

def list_mcp_packages(actions):
    """
    iterate all the actions and return a list of all the packages where there is at least one action with an annotation starting with mcp:
    """
    mcp_packages = set()
    for action in actions:
        for annotation in action.get("annotations", []):
            if isinstance(annotation, dict) and annotation.get("key", "").startswith("mcp:"):
                namespace = action["namespace"].split("/")[-1]
                #print(f"Found  {annotation} in", namespace, action['name'])
                mcp_packages.add(namespace)
                break
    return mcp_packages


def install_mcpjson(package, file, uninstall):
    """
    read the file as json, add an entry <package> under mcpServers with
    commnds: ops
    args: mcp run <package>
    save the file
    """

    # Read existing config or create new one
    if Path(file).exists():
        config = json.loads(Path(file).read_text())
    else:
        config = {"mcpServers": {}}

    #print("BEFORE", json.dumps(config, indent=2))

    cmd = shutil.which("ops")
    if not cmd: 
        raise RuntimeError("ops command not found, please install it first")
    
    if uninstall:
        if package in config["mcpServers"]:
            del config["mcpServers"][package]
            print(f"Removed {package} in {file}")
    else:
        config["mcpServers"][package] = {
            "command": cmd,
            "name": package,
            "args": ["mcp", "run", package],
            "env": {
                "APIHOST": os.getenv("APIHOST") or os.getenv("OPSDEV_APIHOST") or "",
                "AUTH": os.getenv("AUTH") or ""
            }
        }

    # Save updated config
    Path(file).write_text(json.dumps(config, indent=2))

    #print("AFTER", json.dumps(config, indent=2))


#print(sys.argv)
[package, uninstall_str, cursor, claude, fire, sse] = sys.argv[1:]

import openwhisk
actions = openwhisk.call("actions")
mcp_packages =  list_mcp_packages(actions)
uninstall = uninstall_str.lower() == "true"

if package == "":
    print("Available packages with MCP actions:")
    for package in sorted(mcp_packages):
        print(f"  {package}")
    sys.exit(0)

if not package in mcp_packages:
    print(f"Package {package} has not mcp action")
    sys.exit(0)

operation = "Uninstalling" if uninstall else "Installing"

if cursor =="true":
    if not os.path.exists(".cursor"):
        print("No .cursor folder found - we expect to find it it in current working directory")
        sys.exit(1)
    config_path = ".cursor/mcp.json"
    print(f"{operation} MCP Server {package} in Cursor in ", config_path)
    os.makedirs(".cursor", exist_ok=True)
    install_mcpjson(package, config_path, uninstall)

if fire == "true":
    system = platform.system()
    if system == 'Windows':
        base_dir = os.getenv('APPDATA') or os.path.join(os.getenv('USERPROFILE') or "", 'AppData', 'Roaming')
        config_path = os.path.join(base_dir, '5ire', 'mcp.json')
    elif system == 'Darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support/5ire')
        config_path = os.path.join(base_dir, 'mcp.json')
    elif system == 'Linux':
        base_dir = os.path.expanduser('~/.config/5ire')
        config_path = os.path.join(base_dir, 'mcp.json')
    else:
        raise RuntimeError(f'Unsupported OS: {system}')
    print(f"{operation} MCP Server {package} in 5ire in ", config_path)
    os.makedirs(base_dir, exist_ok=True)
    install_mcpjson(package, config_path, uninstall)

if claude == "true":
    system = platform.system()
    if system == 'Windows':
        base_dir = os.getenv('APPDATA') or os.path.join(os.getenv('USERPROFILE') or "", 'AppData', 'Roaming')
        config_path = os.path.join(base_dir, 'Claude', 'claude_desktop_config.json')
    elif system == 'Darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support/Claude')
        config_path = os.path.join(base_dir, 'claude_desktop_config.json')
    else:
        raise RuntimeError(f'Unsupported OS: {system}')
    print(f"{operation} MCP Server in Claude in ", config_path)
    os.makedirs(base_dir, exist_ok=True)
    install_mcpjson(package, config_path, uninstall)
