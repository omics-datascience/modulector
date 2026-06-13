# Modulector SDK

Typed Python SDK for the Modulector API. The package contains client helpers for
querying miRNA target interactions, miRNA aliases, methylation sites, disease
associations, drug associations, and PubMed subscriptions without installing the
Django backend dependencies.

## Installation

```bash
pip install modulector-sdk
```

## Usage

```python
from modulector_sdk import get_mirna_details, get_mirna_target_interactions

details = get_mirna_details("hsa-miR-21-5p")
interactions = get_mirna_target_interactions(
    mirna="hsa-miR-21-5p",
    gene="PTEN",
    include_pubmeds=True,
)
```

Set `MODULECTOR_API_BASE_URL` to target a different Modulector deployment:

```bash
MODULECTOR_API_BASE_URL=https://your-modulector.example.org python script.py
```

Every service function also accepts a `base_url` keyword argument for
per-request overrides.

## MCP server

The SDK also installs a Model Context Protocol server that exposes the same
service functions as LLM-callable tools.

For local stdio MCP clients:

```bash
modulector-mcp
```

Example client configuration:

```json
{
  "mcpServers": {
    "modulector": {
      "command": "modulector-mcp"
    }
  }
}
```

For Streamable HTTP clients:

```bash
modulector-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Then connect the client to `http://127.0.0.1:8000/mcp`.

The server includes tools for miRNA target interactions, miRNA details and
aliases, miRNA identifier resolution, methylation site lookup and annotation,
disease associations, drug associations, and PubMed news subscriptions. Use
`MODULECTOR_API_BASE_URL` or each tool's `base_url` argument to target a custom
Modulector deployment.

## Development

Build this SDK from the `sdk/` directory:

```bash
uv build
```

The generated source distribution and wheel are written to `sdk/dist/`.
