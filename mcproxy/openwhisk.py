import sys, os, requests
from requests.auth import HTTPBasicAuth

APIHOST = os.getenv("OPSDEV_APIHOST")
NAMESPACE = os.getenv("OPSDEV_USERNAME")
AUTH = os.getenv("AUTH")
if AUTH is None:
    print("You are not logged in. Please run 'ops ide login' to login.")
    sys.exit(1) 

ops_auth = HTTPBasicAuth(AUTH.split(":")[0], AUTH.split(":")[1])

def call(cmd, args=None):
    url = f"{APIHOST}/api/v1/namespaces/{NAMESPACE}/{cmd}"
    try:
        if args:
            response = requests.post(url, auth=ops_auth, json=args)
        else:
            response = requests.get(url, auth=ops_auth)
        return response.json()
    except Exception as e:
        print(e)
        return None

