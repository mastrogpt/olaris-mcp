#  olaris-mcp

An ops plugin to create  MCP servers with Apache OpenServerless.

This plugin allows to write an MCP server in a serverless way, just writing functions and publishing them to OpepServerless.

The plugin can be run locally or deployed in a server.

Important: a single mcp server is equivalent to a package`. An MCP server is actually a collection of tools, prompts and resources. Each of those is equivalent to a diffent OpenServerless function.

# Installation

This is a `ops` plugin and can be installed with:

```
ops -plugin https://github.com/mastrogpt/olaris-mcp
```

You can also install locally with:

```
git clone https://github.com/mastrogpt/olaris-mcp
```

Test it has been installed properly with `ops mcp` and ensure you see the synopsis

```
Usage:
 mcp new <package> [<description>] (--tool=<tool>|--resource=<resource>|--prompt=<prompt>|--clean=<clean>) [--redis] [--postgres] [--milvus] [--s3]
 mcp run <package> [--sse]
 mcp generate <package>
 mcp test <package> [--sample] [--norun]
 mcp install [<package>] [--cursor] [--claude] [--5ire] [--uninstall]
 mcp inspect <package>  [--sse] 
 mcp sse <package> [<hostname>] [--uninstall]
```

As you can see you can do:

- `ops mcp new` to  create a new `--tool` or a `--promot` or a  `--resource` in a package 
- `ops mcp run` to  run a package as mcp sever
- `ops mcp test` to test the generated mcp server with cli
- `ops mcp install`  to  install/uninstall local mcp server to cursor / claude / 5ire
- `ops mcp inspect`  to run the  start the MCP web inspector 

# Create a new MCP server

Let's go through the steps to create a simple MCP server, for example one providing wheather informations for any place in the world.

We will create for this a serverless function that can act as a Proxy.

```
ops mcp new demomcp --tool=weather
```

Now you have to provide meta data informations describing your MCP tool with annotations as follows:

```
#-a mcp:type tool
#-a mcp:desc "Provide whether information for a given location"
#-a input:str "the location to get the weather info for"
```

## Implementing a wheather function

Now you can implement the logic or your wheater function

Of course you can use AI to quicky generate your code. For example you can use the following prompt to quickly get a function that retrieves the wheater informatons:

  A python function `get_wheater(location)`,  using `requests` and `open-meteo.com` that will retrieve the location provided in input, consider the first location returned, then ask and return return wheather informations at that location.

I am not including the function here but ChatGPT generally returns a proper implementation you can use.

Hence you can write the following code to invoke it:

```
def weather(args):
  inp = args.get("input", "")
  out = f"Please provide a location to get the weather information for."
  if inp != "":
    out = get_wheater(inp)
  return { "output": out }
```

Deploy the function and test is as follows:

```
$ ops ide deploy demomcp/weather
ok: updated action demomcp/weather
$  ops invoke demomcp/weather 
{
    "output": "Please provide a location to get the weather information for."
}
$ ops invoke demomcp/weather input=Rome
{
    "output": {
        "location": "Rome, Italy",
        "temperature": 26.0,
        "time": "2025-06-22T06:45",
        "weathercode": 2,
        "winddirection": 360,
        "windspeed": 2.9
    }
}
$ ops invoke demomcp/weather input=NotExitingCity
{
    "output": "Could not find location: NotExitingCity"
}
```

# Deploy as an MCP Server

Your MCP server is basically ready, and you can test it with the graphical inspector as follows:

![](inspect-mcpserver.png)












