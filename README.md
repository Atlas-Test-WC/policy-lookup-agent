# Policy Lookup Agent

A minimal project that shows how an AI agent, an MCP server, tools, prompts, and a simple data source work together.


In this project, `agent.py` is the agent. It:

1. Reads your question
2. Sends it to an LLM with a system prompt
3. Lets the LLM choose when to call MCP tools
4. Returns the final answer


## Available Tools

The MCP server exposes exactly two tools:

| Tool | Description |
|------|-------------|
| `lookup_policy(policy_name)` | Returns the answer for a named policy |
| `list_policies()` | Returns all available policy names |

The tool logic is implemented in:

- `mcp_server/tools/lookup_policy.py`
- `mcp_server/tools/list_policies.py`

## How the CSV Is Used

`policies.csv` is the knowledge base. It has two columns:

- `policy` — the policy name (for example, `PTO`)
- `answer` — the policy text

Both tools read this file directly. There is no database, search index, or vector store. The tools load the CSV, find the matching row, and return the result.

## Architecture

```
User
  ↓
Agent (agent.py)
  ↓
LLM (via LiteLLM)
  ↓
MCP Server (mcp_server/server.py)
  ↓
Tools (lookup_policy, list_policies)
  ↓
policies.csv
```

### Flow

1. The user asks a question in the terminal.
2. The agent sends the question and system prompt to the LLM.
3. If the LLM needs policy data, it requests a tool call.
4. The agent forwards the tool call to the MCP server.
5. The MCP tool reads `policies.csv` and returns the result.
6. The agent sends the tool result back to the LLM.
7. The LLM produces the final answer for the user.

## Project Structure

```
policy-lookup-agent/
├── README.md
├── requirements.txt
├── agent.py
├── policies.csv
├── prompts/
│   └── system_prompt.txt
└── mcp_server/
    ├── server.py
    └── tools/
        ├── lookup_policy.py
        └── list_policies.py
```

## Setup

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Optional: choose a different model:

```bash
export LITELLM_MODEL="gpt-4o"
```

## Run the Agent

```bash
python agent.py
```

## Example Interactions

**User:** What is the PTO policy?

**Agent:** Employees receive 20 days of PTO annually.

**User:** What policies are available?

**Agent:** PTO, Remote Work, Travel

## Run the MCP Server Alone

You can also run the MCP server directly for testing with MCP-compatible clients:

```bash
cd mcp_server
python server.py
```

## Design Notes

This project is intentionally small:

- CSV file instead of a database
- Two focused tools instead of many abstractions
- System prompt stored separately in `prompts/system_prompt.txt`
- LiteLLM for model access
- Official Python MCP SDK for the server and client

The goal is clarity, not production readiness.
