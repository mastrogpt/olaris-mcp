import sys, os
from pathlib import Path

def write_text_or_clean(file, clean, text):
    path = Path(file)
    if clean:
        if path.exists():
            print(f"Cleaning file {file}")
            path.unlink()
        return
    if path.exists():
        print(f"File {file} already exists.")
        return
    print(f"Creating file {file}")
    path.write_text(text)

def get_annotations(opts):
    annotations = []
    if opts["redis"]:
        annotations += ['#-p REDIS_URL "$REDIS_URL"', '#-p REDIS_PREFIX "$REDIS_PREFIX"']
    if opts["postgres"]:
        annotations += ['#-p POSTGRES_URL "$POSTGRES_URL"']
    if opts["milvus"]:
        annotations += ['#-p MILVUS_HOST "MILVUS_HOST"', '#-p MILVUS_DB_NAME "$MILVUS_DB_NAME"', '#-p MILVUS_TOKEN "$MILVUS_TOKEN"']
    if opts["s3"]:
        annotations += ['#-p S3_HOST "$S3_HOST"','#-p S3_PORT "$S3_PORT"','#-p S3_ACCESS_KEY "$S3_ACCESS_KEY"','#-p S3_SECRET_KEY "$S3_SECRET_KEY"', '#-p S3_BUCKET_DATA "$S3_BUCKET_DATA"']
    return "\n".join(annotations)   

def get_imports(opts):
    imports = ["import os"]
    if opts["redis"]:
        imports.append("import redis")
    if opts["postgres"]:
        imports.append("import psycopg")
    if opts["milvus"]:
        imports.append("import pymilvus")
    if opts["s3"]:
        imports.append("import boto3")
    return "\n".join(imports)

def get_inits(opts):
    inits = []
    if opts["redis"]:
        inits.append("""  # connecting to redis
  rd = redis.from_url(args.get("REDIS_URL", os.getenv("REDIS_URL")))
  prefix = args.get("REDIS_PREFIX", os.getenv("REDIS_PREFIX"))
""")
    if opts["postgres"]:
        inits.append("""  # conecting to postgres
  db = psycopg.connect(args.get("POSTGRES_URL", os.getenv("POSTGRES_URL")))
  # remember this after using the connection
  db.commit()                     
  db.close()
""")
    if opts["milvus"]:
        inits.append("""  # connecting to milvus
  uri = f"http://{args.get("MILVUS_HOST", os.getenv("MILVUS_HOST"))}"
  token = args.get("MILVUS_TOKEN", os.getenv("MILVUS_TOKEN"))    
  db_name = args.get("MILVUS_DB_NAME", os.getenv("MILVUS_DB_NAME"))
  vdb = MilvusClient(uri=uri, token=token, db_name=db_name)
""")
    if opts["s3"]:
        inits.append("""  # connecting to s3
  s3host = args.get("S3_HOST", os.getenv("S3_HOST"))
  s3port = args.get("S3_PORT", os.getenv("S3_PORT"))
  s3url = f"http://{s3host}:{s3port}"
  s3key = args.get("S3_ACCESS_KEY", os.getenv("S3_ACCESS_KEY"))
  s3sec = args.get("S3_SECRET_KEY", os.getenv("S3_SECRET_KEY"))
  s3store = boto3.client('s3', region_name='us-east-1', endpoint_url=s3url, aws_access_key_id=s3key, aws_secret_access_key=s3sec )
  s3bucket =args.get("S3_BUCKET_DATA", os.getenv("S3_BUCKET_DATA"))
""")
    return "\n".join(inits)
    
def main(typ, package, name, description, opts):
    print(f"Type: {typ}")
    print(f"Package: {package}")
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Options: {opts}")
    
    dir = os.getenv("OPS_PWD")
    if dir:
        os.chdir(dir)
    clean = typ == "clean"

    os.makedirs(f"packages/{package}/{name}", exist_ok=True)
    os.makedirs(f"tests/{package}", exist_ok=True)

    annotation = get_annotations(opts)
    imports = get_imports(opts)
    inits = get_inits(opts)

    file = Path(f"packages/{package}/{name}/__main__.py")
    write_text_or_clean(file, clean, f"""#--kind python:default
#--web true
#-a mcp:type {typ}
#-a mcp:desc "{description}"
#-a input:str "the user input (default='')"
#-p REDIS_URL "$REDIS_URL"
#-p REDIS_PREFIX "$REDIS_PREFIX"
{annotation}
import {name}

def main(args):
  # invoked as web action
  if "__ow_method" in args:
    import os, redis
    [user, secret] = args.get("token", "_:_").split(":")
    rd = redis.from_url(args.get("REDIS_URL"))
    check = rd.get(f"{{args.get("REDIS_PREFIX")}}TOKEN:{{user}}") or b''
    if check.decode('utf-8') == secret:
        return {{"body": {name}.{name}(args)}}
    return {{"body": "unauthorized"}}
  # CLI access
  return {name}.{name}(args)
""")

    file = f"packages/{package}/{name}/{name}.py"
    write_text_or_clean(file, clean, f"""{imports}
def {name}(args):
  input = args.get("input", "")
{inits}
  output = input
  return {{ "output": output }}
""")

    file = Path(f"tests/{package}/test_{name}.py")
    write_text_or_clean(file, clean, f"""import sys
sys.path.append("packages/{package}/{name}")
import {name} as m

def test_{name}():
    args = {{}}
    result = m.{name}(args)
    assert result["output"] == ""
    args = {{"input": "test input"}}
    result = m.{name}(args)
    assert result["output"] == "test input"
""")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: <type> <package> <name> <description>")
        sys.exit(0)

    opts = {
        "redis":    os.getenv("NEW_REDIS") == "true", 
        "postgres": os.getenv("NEW_POSTGRES") == "true", 
        "milvus":   os.getenv("NEW_MILVUS") == "true", 
        "s3":       os.getenv("NEW_S3") == "true", 
    }
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], opts)
