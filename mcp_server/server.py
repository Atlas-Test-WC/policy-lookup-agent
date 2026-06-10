from mcp.server.fastmcp import FastMCP

from tools.list_policies import list_policies as _list_policies
from tools.lookup_policy import lookup_policy as _lookup_policy

mcp = FastMCP("Policy Lookup")


@mcp.tool()
def lookup_policy(policy_name: str) -> str:
    """Returns the answer associated with a policy."""
    return _lookup_policy(policy_name)


@mcp.tool()
def list_policies() -> list[str]:
    """Returns all available policy names."""
    return _list_policies()


if __name__ == "__main__":
    mcp.run(transport="stdio")
