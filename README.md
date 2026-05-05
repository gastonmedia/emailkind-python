# emailkind

[![PyPI version](https://img.shields.io/pypi/v/emailkind.svg)](https://pypi.org/project/emailkind/)
[![Python versions](https://img.shields.io/pypi/pyversions/emailkind.svg)](https://pypi.org/project/emailkind/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The official Python SDK for the [EmailKind](https://emailkind.com) API.

Classify any email address in one API call. Get the provider (Google Workspace, Microsoft 365, Zoho, 150+ others), classification flags (business, personal, disposable, education), company enrichment, and a confidence score.

## Installation

```bash
pip install emailkind
```

## Quick start

```python
from emailkind import EmailKind

client = EmailKind("sk_live_xxx")

result = client.classify(email="ceo@stripe.com")

print(result.provider.name)            # "Google Workspace"
print(result.provider.type)            # "business"
print(result.classification.is_business)  # True
print(result.confidence)               # 0.98
```

## What you get back

Every classify call returns a rich, structured result:

```python
result = client.classify(email="ceo@stripe.com", enrich=True)

# Provider detection — not just "Google", but Google Workspace vs Gmail
result.provider.id          # "google_workspace"
result.provider.name        # "Google Workspace"
result.provider.type        # "business"

# Classification flags
result.classification.is_business       # True
result.classification.is_free           # False
result.classification.is_disposable     # False
result.classification.is_education      # False

# Company enrichment (when enrich=True)
result.company.name         # "Stripe, Inc."
result.company.source       # "ssl"

# Confidence score
result.confidence           # 0.98

# Raw MX records
result.mx                   # ["aspmx.l.google.com", ...]
```

## Configuration

```python
from emailkind import EmailKind

# From argument
client = EmailKind("sk_live_xxx")

# From environment variable
# export EMAILKIND_API_KEY=sk_live_xxx
client = EmailKind()

# Custom options
client = EmailKind(
    api_key="sk_live_xxx",
    base_url="https://custom.example.com",  # self-hosted
    timeout=10,                              # seconds (default: 30)
)
```

## Classify

```python
# By email
result = client.classify(email="user@gmail.com")

# By domain
result = client.classify(domain="stripe.com")

# With company enrichment
result = client.classify(email="ceo@stripe.com", enrich=True)
print(result.company.name)  # "Stripe, Inc."
```

## Batch classification

Classify up to 100 emails or domains in a single request:

```python
batch = client.classify_batch(
    emails=["ceo@stripe.com", "user@gmail.com"],
    domains=["notion.so"],
    enrich=True,
)

for item in batch.results:
    print(f"{item.input} -> {item.provider.name} ({item.provider.type})")

# ceo@stripe.com -> Google Workspace (business)
# user@gmail.com -> Gmail (personal)
# notion.so -> Cloudflare (business)
```

## Custom rules

Override classifications for specific domains or MX patterns (paid plans):

```python
# List rules
rules = client.list_rules()

# Create a rule
rule = client.create_rule(
    match_type="domain",
    match_value="internal.company.com",
    provider_name="Internal Mail",
    provider_type="business",
)

# Delete a rule
client.delete_rule(rule.id)
```

## Bulk processing

Upload a CSV for async classification of large datasets (paid plans):

```python
# Upload a file
job = client.bulk_upload("emails.csv", enrich=True)
print(job.id, job.status)  # "abc123" "pending"

# Check progress
status = client.bulk_status(job.id)
print(f"{status.processed}/{status.total}")  # "4521/10000"

# Download results when completed
csv_bytes = client.bulk_results(job.id)
with open("results.csv", "wb") as f:
    f.write(csv_bytes)

# List all jobs
jobs = client.bulk_list()
```

## Error handling

All API errors raise typed exceptions with structured context:

```python
from emailkind import (
    EmailKindError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ForbiddenError,
    NotFoundError,
)

try:
    result = client.classify(email="user@example.com")
except AuthenticationError:
    # Invalid or missing API key (401)
    pass
except RateLimitError as e:
    # Too many requests (429)
    print(f"Retry after {e.retry_after}s")
except ValidationError:
    # Bad request parameters (400)
    pass
except ForbiddenError:
    # Plan doesn't support this feature (403)
    pass
except NotFoundError:
    # Resource not found (404)
    pass
except EmailKindError as e:
    # Catch-all for any API error
    print(e.status_code, e.code, e.message, e.request_id)
```

Every exception exposes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error description |
| `code` | `str` | Machine-readable error code |
| `status_code` | `int` | HTTP status code |
| `request_id` | `str` | Unique ID for support |
| `retry_after` | `int` | Seconds to wait (only on `RateLimitError`) |

## Sandbox mode

Use test keys to develop without affecting your quota:

```python
client = EmailKind("sk_test_xxx")
result = client.classify(email="user@gmail.com")
# Works identically, but usage is not tracked
```

## Requirements

- Python 3.8+
- [`requests`](https://docs.python-requests.org/) (installed automatically)

## Other SDKs

| Language | Package |
|----------|---------|
| Node.js | [`emailkind`](https://www.npmjs.com/package/emailkind) |
| Go | [`emailkind-go`](https://pkg.go.dev/github.com/gastonmedia/emailkind-go) |
| REST | [API docs](https://emailkind.com/docs) |

## License

MIT
