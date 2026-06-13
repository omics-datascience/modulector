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

## Development

Build this SDK from the `sdk/` directory:

```bash
uv build
```

The generated source distribution and wheel are written to `sdk/dist/`.
