from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.responses import HTMLResponse,Response
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

# HTML for the homepage that displays "MCP Server"
async def homepage(request: Request) -> HTMLResponse:
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Server</title>
        <link href="https://fonts.googleapis.com/css2?family=Comfortaa&display=swap" rel="stylesheet">
        <style>    
            body {
                font-family: 'Comfortaa', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #1EA1CE; color: #fff }
            h1 { margin-bottom: 10px; }            
            #logo { width: 204px; height: auto; margin: 0 auto; display: block; }
            code { background-color: #133e52; padding: 2px 4px; border-radius: 4px; color: #fff; }
            .content { text-align: center; margin-top: 50px; }
        </style>
    </head>
    <body>
        <div id="app">
            <div id="logo">
                <svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="120 220 560 130" class="my-1 h-16 w-52 rounded-lg transition-all duration-300 ease-in-out hover:bg-surface-400" style="shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd" xmlns:xlink="http://www.w3.org/1999/xlink"><g><path style="opacity:0.807" fill="#fefffe" d="M 210.5,236.5 C 224.732,234.977 237.732,238.144 249.5,246C 258.189,255.632 260.856,266.799 257.5,279.5C 271.319,282.472 276.486,290.806 273,304.5C 271.167,306.333 269.333,308.167 267.5,310C 265.5,310.667 263.5,310.667 261.5,310C 260.941,309.275 260.608,308.442 260.5,307.5C 262.439,304.385 264.606,301.385 267,298.5C 267.306,292.297 264.473,288.131 258.5,286C 255.487,285.498 252.487,284.998 249.5,284.5C 250.176,278.963 251.176,273.463 252.5,268C 251.181,256.027 244.847,248.027 233.5,244C 223.485,240.737 213.485,240.737 203.5,244C 199.928,245.569 196.928,247.902 194.5,251C 188.843,251.499 183.176,251.666 177.5,251.5C 177.36,249.876 178.027,248.71 179.5,248C 186.879,248.798 192.879,246.464 197.5,241C 201.846,239.164 206.179,237.664 210.5,236.5 Z"></path></g><g><path style="opacity:0.896" fill="#fefffe" d="M 470.5,252.5 C 473.961,252.146 476.461,253.479 478,256.5C 478.333,269.5 478.667,282.5 479,295.5C 481.956,297.501 484.956,299.501 488,301.5C 489.12,304.999 488.287,307.833 485.5,310C 476.795,311.731 470.629,308.564 467,300.5C 465.425,286.547 465.091,272.547 466,258.5C 466.599,255.746 468.099,253.746 470.5,252.5 Z"></path></g><g><path style="opacity:0.805" fill="#fefffe" d="M 192.5,258.5 C 199.589,258.116 206.589,258.616 213.5,260C 221.578,263.823 226.244,270.156 227.5,279C 232.806,279.243 237.806,280.576 242.5,283C 247.196,289.17 247.529,295.503 243.5,302C 242.207,302.49 240.873,302.657 239.5,302.5C 240.853,299.907 241.519,297.073 241.5,294C 241.873,287.706 238.873,284.706 232.5,285C 228.848,284.501 225.182,284.335 221.5,284.5C 219.462,266.799 209.795,260.632 192.5,266C 187.246,267.627 182.58,270.294 178.5,274C 177.5,274.667 176.5,274.667 175.5,274C 174.424,272.274 174.257,270.441 175,268.5C 179.946,263.449 185.779,260.115 192.5,258.5 Z"></path></g><g><path style="opacity:0.893" fill="#fefffe" d="M 300.5,266.5 C 315.386,264.253 324.886,270.253 329,284.5C 329.667,291.5 329.667,298.5 329,305.5C 326.043,311.289 322.043,311.956 317,307.5C 316.667,300.167 316.333,292.833 316,285.5C 310,276.167 304,276.167 298,285.5C 297.934,293.271 297.267,300.938 296,308.5C 292.667,311.167 289.333,311.167 286,308.5C 284.057,299.205 284.057,289.872 286,280.5C 288.774,273.557 293.607,268.89 300.5,266.5 Z"></path></g><g><path style="opacity:0.892" fill="#fefffe" d="M 336.5,266.5 C 339.97,265.875 342.804,266.875 345,269.5C 345.098,277.577 345.765,285.577 347,293.5C 353.526,300.41 359.193,299.743 364,291.5C 364.066,283.729 364.733,276.062 366,268.5C 369.333,265.833 372.667,265.833 376,268.5C 377.601,276.395 377.934,284.395 377,292.5C 372.9,306.907 363.4,312.741 348.5,310C 336.092,304.701 330.758,295.201 332.5,281.5C 332.667,278.167 332.833,274.833 333,271.5C 333.257,269.093 334.424,267.427 336.5,266.5 Z"></path></g><g><path style="opacity:0.901" fill="#fefffe" d="M 383.5,266.5 C 387.287,265.814 390.454,266.814 393,269.5C 394.688,274.74 396.855,279.74 399.5,284.5C 401.762,279.551 403.928,274.551 406,269.5C 410.399,265.346 414.399,265.679 418,270.5C 418.667,271.833 418.667,273.167 418,274.5C 414.333,284.167 410.667,293.833 407,303.5C 404.694,310.6 400.361,312.267 394,308.5C 389.667,297.167 385.333,285.833 381,274.5C 380.388,271.389 381.221,268.723 383.5,266.5 Z"></path></g><g><path style="opacity:0.907" fill="#fefffe" d="M 505.5,266.5 C 525.611,265.612 534.944,275.279 533.5,295.5C 533.333,299.167 533.167,302.833 533,306.5C 530.947,310.292 527.781,311.458 523.5,310C 521.663,308.52 519.663,308.52 517.5,310C 500.866,312.197 491.2,305.03 488.5,288.5C 489.741,277.609 495.407,270.276 505.5,266.5 Z M 507.5,279.5 C 517.878,279.031 521.712,283.698 519,293.5C 514.193,299.138 509.193,299.471 504,294.5C 500.387,288.391 501.553,283.391 507.5,279.5 Z"></path></g><g><path style="opacity:0.888" fill="#fefffe" d="M 554.5,266.5 C 562.163,265.042 565.663,268.042 565,275.5C 560.259,278.021 555.592,280.687 551,283.5C 549.765,291.423 549.098,299.423 549,307.5C 546.441,310.349 543.274,311.183 539.5,310C 538.299,309.097 537.465,307.931 537,306.5C 535.896,297.011 536.562,287.677 539,278.5C 542.644,272.335 547.811,268.335 554.5,266.5 Z"></path></g><g><path style="opacity:0.875" fill="#fefffe" d="M 571.5,266.5 C 576.118,265.949 578.951,267.949 580,272.5C 580.667,283.5 580.667,294.5 580,305.5C 578.551,310.218 575.385,311.718 570.5,310C 569.667,309.167 568.833,308.333 568,307.5C 567.333,295.167 567.333,282.833 568,270.5C 568.69,268.65 569.856,267.316 571.5,266.5 Z"></path></g><g><path style="opacity:0.927" fill="#fefffe" d="M 593.5,266.5 C 601.174,266.334 608.841,266.5 616.5,267C 619.287,269.167 620.12,272.001 619,275.5C 618.5,276.667 617.667,277.5 616.5,278C 610.167,278.333 603.833,278.667 597.5,279C 596.167,280 596.167,281 597.5,282C 602.833,282.333 608.167,282.667 613.5,283C 621.873,288.801 623.707,296.301 619,305.5C 617.269,307.617 615.102,309.117 612.5,310C 604.5,310.667 596.5,310.667 588.5,310C 584.5,306.333 584.5,302.667 588.5,299C 594.5,298.667 600.5,298.333 606.5,298C 608.481,297.395 608.815,296.395 607.5,295C 594.464,297.998 586.464,293.165 583.5,280.5C 584.171,273.843 587.505,269.176 593.5,266.5 Z"></path></g><g><path style="opacity:0.903" fill="#fefffe" d="M 434.5,267.5 C 453.822,266.323 462.989,275.323 462,294.5C 457.829,307.316 448.996,312.816 435.5,311C 421.971,306.79 416.471,297.624 419,283.5C 421.685,275.65 426.852,270.316 434.5,267.5 Z M 439.5,279.5 C 449.623,281.793 452.123,287.459 447,296.5C 438.479,300.985 432.979,298.485 430.5,289C 431.683,283.987 434.683,280.82 439.5,279.5 Z"></path></g><g><path style="opacity:0.804" fill="#fefffe" d="M 188.5,280.5 C 191.187,280.336 193.854,280.503 196.5,281C 198.032,283.33 197.698,285.33 195.5,287C 182.802,287.792 170.135,287.459 157.5,286C 156.185,284.605 156.519,283.605 158.5,283C 168.654,282.164 178.654,281.331 188.5,280.5 Z"></path></g><g><path style="opacity:0.822" fill="#fefffe" d="M 192.5,290.5 C 196.269,291.424 197.269,293.59 195.5,297C 182.484,297.687 169.484,297.52 156.5,296.5C 156.5,295.5 156.5,294.5 156.5,293.5C 168.632,292.308 180.632,291.308 192.5,290.5 Z"></path></g><g><path style="opacity:0.834" fill="#fefffe" d="M 188.5,301.5 C 194.662,300.156 196.662,302.322 194.5,308C 182.145,308.728 169.812,308.562 157.5,307.5C 157.5,306.5 157.5,305.5 157.5,304.5C 167.995,303.668 178.329,302.668 188.5,301.5 Z"></path></g></svg>
            </div>
            <div class="content">
                <h1>MCP Server {package}</h1>
                <p>Server <i>{package}</i> is running correctly.<br/><br/>
                Run <code>ops a41 mcp inspect</code> in a terminal to try it</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

# favicon endpoint to serve a static favicon 
async def empty_favicon(request):
    return Response(status_code=204)
        

# Create Starlette application with SSE transport
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/", endpoint=homepage),
            Route("/favicon.ico", endpoint=empty_favicon),
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    sse = True
    # Create and run Starlette app
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host="0.0.0.0", port=8080,  timeout_graceful_shutdown=20, lifespan="auto")