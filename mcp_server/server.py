from mcp.server import FastMCP


mcp = FastMCP("demo")


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the weather in a given city"""
    return f"The weather in {city} is sunny"


@mcp.tool()
async def get_my_github_repo_url() -> str:
    """
    查询我的github仓库url
    """
    return "https://github.com/FBamx?tab=repositories"

if __name__ == "__main__":
    mcp.run()

