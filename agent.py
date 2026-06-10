#!/usr/bin/env python3
"""Simple policy lookup agent using LiteLLM and an MCP server."""

import asyncio
import json
import os
import sys
from pathlib import Path

import litellm
from litellm import experimental_mcp_client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.txt"
MCP_SERVER_PATH = PROJECT_ROOT / "mcp_server" / "server.py"
DEFAULT_MODEL = os.environ.get("LITELLM_MODEL", "gpt-4o-mini")


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def extract_tool_result_content(result) -> str:
    """Convert an MCP tool result into plain text for the LLM."""
    parts = []
    for block in result.content:
        if hasattr(block, "text"):
            parts.append(block.text)
        else:
            parts.append(str(block))
    return "\n".join(parts) if parts else str(result.content)


async def run_agent_turn(session: ClientSession, tools: list, messages: list) -> str:
    """Send messages to the LLM, run any tool calls, and return the final answer."""
    while True:
        response = await litellm.acompletion(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        assistant_message = message.model_dump(exclude_none=True)
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls")
        if not tool_calls:
            return assistant_message.get("content", "")

        for tool_call in tool_calls:
            result = await experimental_mcp_client.call_openai_tool(
                session=session,
                openai_tool=tool_call,
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": extract_tool_result_content(result),
                }
            )


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "Set OPENAI_API_KEY before running the agent.\n"
            "Optional: set LITELLM_MODEL to choose a different model.",
            file=sys.stderr,
        )
        sys.exit(1)

    system_prompt = load_system_prompt()
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_PATH)],
        cwd=str(PROJECT_ROOT / "mcp_server"),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await experimental_mcp_client.load_mcp_tools(
                session=session,
                format="openai",
            )

            print("Policy Lookup Agent")
            print("Ask about company policies. Type 'quit' to exit.\n")

            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye.")
                    break

                if not user_input:
                    continue
                if user_input.lower() in {"quit", "exit"}:
                    print("Goodbye.")
                    break

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ]

                try:
                    answer = await run_agent_turn(session, tools, messages)
                    print(f"\nAgent: {answer}\n")
                except Exception as error:
                    print(f"\nAgent error: {error}\n", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
