@mcp.tool(description="Reverse the input text")
def reverse_local(input: str) -> str:
    """
    input is the string to reverse
    """
    output = input[::-1]
    return output

@mcp.resource("lgreet://{input}")
def greet_local(input: str) -> str:
    """
    input is the name to greet
    """
    output = input or "world"
    return f"Hello, {output}!"

@mcp.prompt(description="who you are")
def person_local(input: str) -> str:
    """
    input is the description of the person
    """
    output = input or "a nice person"
    return f"You are {output}!"

