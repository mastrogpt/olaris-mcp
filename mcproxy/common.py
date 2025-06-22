PACKAGE="common"

import os
import requests
import traceback
import dotenv
import sys
import signal
import json
from requests.auth import HTTPBasicAuth
from mcp.server.fastmcp import FastMCP
from typing import Dict


def signal_handler(sig, frame):
    """
    Handle system signals to gracefully shut down the server.
    """
    print("Shutting down server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# first load wskprops if there is no AUTH
if os.getenv("AUTH") is None:
    dotenv.load_dotenv(os.path.expanduser("~/.wskprops"))

# get info from the environment
AUTH = os.getenv("AUTH")
if AUTH is None:
    print("You are not logged in. Please run 'ops ide login' to login.")
    sys.exit(1)

APIHOST = os.getenv("APIHOST")
if APIHOST is None:
    print("please set APIHOST in your environment")
    sys.exit(1)
    
ops_auth = HTTPBasicAuth(AUTH.split(":")[0], AUTH.split(":")[1])

NAMESPACE = os.getenv("OPSDEV_USERNAME", None)
if NAMESPACE is None:
    try: 
        NAMESPACE = requests.get(f"{APIHOST}/api/v1/namespaces", auth=ops_auth).json()[0]
        print("Connected to", NAMESPACE)
    except: print("error retrieving namespace")

def invoke(package, func, args):
    if NAMESPACE is None:
        return {"error": "please provide credentials for openserverless"}
    url = f"{APIHOST}/api/v1/namespaces/{NAMESPACE}/actions/{package}/{func}?blocking=true"
    try:
        res = requests.post(url, auth=ops_auth, json=args)
        out = res.json().get("response", {}).get("result", {"error": "no response"})
        return out
    except Exception as e:
        traceback.print_exc()
        return { "error": str(e) }


logfile = os.getenv("LOGFILE")

def log(func, sep, msg):
    if logfile:
        with open(logfile, "a") as f:
            f.write(f"{PACKAGE}/{func} {sep} {json.dumps(msg)}\n")

def info(msg):
    if logfile:
        with open(logfile, "a") as f:
            f.write(f"{PACKAGE} {msg}\n")

info("Starting mcproxy server")

mcp = FastMCP(name=PACKAGE)

