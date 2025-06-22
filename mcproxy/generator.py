import os, sys, requests
from pathlib import Path

import openwhisk
    
COMMON = Path("common.py").read_text()
SAMPLE = Path("sample.py").read_text()
SSE = Path("sse.py").read_text()

def extract_types(actions, package):
    """
    Extract function annotations from actions matching the target namespace and having mcp:type.
    """
    # Initialize result map
    result = {}
    
    # Expected namespace for filtering
    target_namespace = f"{openwhisk.NAMESPACE}/{package}"
    
    # Process each action
    for action in actions:
        # Skip if not in target namespace
        if action['namespace'] != target_namespace:
            continue
            
        # Get annotations
        annotations = action.get('annotations', [])
        
        # Check if this action has mcp:type annotation
        has_mcp_type = any(ann.get('key') == 'mcp:type' for ann in annotations)
        if not has_mcp_type:
            continue
            
        # Get function name
        func_name = action['name']
        
        # Create annotation map for this function
        ann_map = {}
        for ann in annotations:
            key = ann.get('key', '')
            # Include annotations with ':' in the key, but exclude mcp:type
            if ':' in key:
                ann_map[key] = ann.get('value')
                
        # Add to result if we found any matching annotations
        if ann_map:
            result[func_name] = ann_map
    
    return result

def config(package):
    # Get the current working directory
    dir = os.path.abspath(os.getcwd())
    # Create mcp folder if it doesn't exist
    os.makedirs('_svr', exist_ok=True)

    # Generate config file path
    filepath = f'_svr/{package}.json'
    Path(filepath).write_text(f"""{{ "mcpServers": {{
    "{package}": {{
      "command": "uv",
      "args": ["--directory", "{dir}", "run", "mcp", "run", "_svr/{package}.py"],
      "env": {{
          "LOGFILE": "_svr/{package}.log",
          "APIHOST": "{os.getenv("APIHOST") or ""}",
          "AUTH": "{os.getenv("AUTH") or ""}"
      }}
    }}
  }}
}}
""")


def extract_default(ann_value):
    """
    Looks for (default=XXX) in the ann_value, returns the value XXX or None if not found.
    """
    if not ann_value or "(default=" not in ann_value:
        return None
    start = ann_value.find("(default=") + len("(default=")
    end = ann_value.find(")", start)
    return ann_value[start:end] if end != -1 else None

def generate(types, package, sample):
    """
    Create a folder mcp if it does not exist and generate a file mcp/<package>.py.
    Write the common code to the file then iterate over the keys of the types.
    Look at the values, for each key consider <annotation> as:
    - @mcp.tool if the value is "tool"
    - @mcp.prompt if the value is "prompt" 
    - @mcp.resource(<value>) if the value is "resource" <value> is the value of mcp:resource
    Initialize <docs> with the value of mcp:desc
    Construct as array <args>, <docs>, <vars> by iterating <current> the values of the types[<key>] as follows:
    - exclude anything starting with "mcp:"
    - add to <args> the <current>
    - add to <vars> the <current> without what is after the ":"
    - add to <docs> the <current> " is " + value of <current>
    Then add a "def <key>(<args converted to a comma separated string>)" with the <annotation>
    Finally add <docs> as a docstring to the function, concatenating all the docs with a newline.
    The body should create a message dictionary, assign each of <vars> in a key with the name of the var, then execute a 'invoke(<func>, <message>)
    """
    # Create mcp folder if it doesn't exist
    os.makedirs('_svr', exist_ok=True)
    
    # Generate file path
    filepath = f'_svr/{package}.py'
    
    #f = open(filepath, 'w')
    with open(filepath, 'w') as f:
        # Write common code
        f.write(COMMON.replace("\"common\"", f"\"{package}\""))

        if sample:
            f.write(SAMPLE)

        # Process each function
        items = list(types.items())
        for key, annotations in items:
            #(key, annotations) = items[0]
            # Get annotation type
            mcp_type = annotations.get('mcp:type')
            res_to_out = "out = res"
            result_type = "Dict"
            description = annotations.get('mcp:desc')
            
            # Build args, vars and docs arrays
            docs = []
            args = []
            vars = []
            for ann_key, ann_value in annotations.items():
                if not ann_key.startswith('mcp:'):
                    var = ann_key.split(':')[0]
                    default_value = extract_default(ann_value)
                    if default_value:
                        ann_key += f"={default_value}"
                        args.append(ann_key)
                    else:
                        args.insert(0, ann_key)
                    vars.append(var)
                    docs.append(f"- Parameter {var}: {ann_value}")

            # Determine decorator
            if mcp_type == 'tool':
                decorator = '@mcp.tool('
                if description:
                    decorator += f'description="{description}"'
                decorator +=')\n'
            elif mcp_type == 'prompt':
                decorator = '@mcp.prompt('
                if description:
                    decorator += f'description="{description}"'
                decorator +=')\n'
                res_to_out = "out = res.get('output', 'no output')"
                result_type = "str"
            elif mcp_type == 'resource':
                decorator = f'@mcp.resource("{key}://{{{vars[0]}}}")\n'
                res_to_out = "out = res.get('output', 'no output')"
                result_type = "str"
            else:
                continue
                
            if description:
                docs.insert(0,description)
            
            
            # Write function
            f.write(decorator)
            f.write(f'def {key}({",".join(args)}) -> {result_type}:\n')
            f.write('    """\n')
            f.write('    ' + '\n    '.join(docs) + '\n')
            f.write('    """\n')
            f.write('    message = {}\n')
            for arg, var in zip(args, vars):
                f.write(f'    if {var}: message["{var}"] = {var}\n')
            f.write(f'    if logfile: log("{key}", ">>>", message)\n')
            f.write(f'    res = invoke(PACKAGE, "{key}", message)\n')
            f.write(f'    if logfile: log("{key}", "<<<", res)\n')
            f.write(f'    {res_to_out}\n')
            f.write(f'    return out\n\n')
    

        #f.write(f'print("Starting", PACKAGE)\n')
        #f.write(f"mcp.run(transport='sse')\n")
        # Write sse code
        f.write(SSE.replace("{package}", package))

def main(package, sample):
    # Get all actions
    
    actions = openwhisk.call("actions")
    types = extract_types(actions, package)
    generate(types, package, sample)
    config(package)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generator.py <package>")
        sys.exit(1)

    sample = len(sys.argv) > 2 and sys.argv[2] == "true"

    main(sys.argv[1], sample)
