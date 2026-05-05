# emailkind

[![PyPI version](https://img.shields.io/pypi/v/emailkind.svg)](https://pypi.org/project/emailkind/)
[![Python versions](https://img.shields.io/pypi/pyversions/emailkind.svg)](https://pypi.org/project/emailkind/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Python SDK to classify email addresses by provider (Gmail vs Google Workspace, Outlook.com vs Microsoft 365), type (business / personal / disposable / education), and company — using only passive DNS analysis.

Unlike email verification APIs that ping mailboxes, EmailKind uses MX, SPF, and TLS certificate analysis to identify the exact provider and type behind any email address — without sending anything. 150+ providers detected, 57,000+ disposable domains tracked, company enrichment included.

## Installation

```bash
pip install emailkind
```

## Get an API key

Free tier with 100 calls/month, no credit card required.

**https://emailkind.com/register**

## Quick start

```python
from emailkind import EmailKind

client = EmailKind("sk_live_xxx")

result = client.classify(email="ceo@stripe.com")

print(result.provider.name)               # "Google Workspace"
print(result.provider.type)               # "business"
print(result.classification.is_business)  # True
print(result.confidence)                  # 0.98
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

## Recipes

### Block disposable email signups in FastAPI

```python
from fastapi import FastAPI, HTTPException
from emailkind import EmailKind

app = FastAPI()
ek = EmailKind()  # reads EMAILKIND_API_KEY from env

@app.post("/signup")
def signup(email: str):
    result = ek.classify(email=email)
    if result.classification.is_disposable:
        raise HTTPException(400, "Disposable emails are not allowed")
    # proceed with registration...
```

### Qualify B2B leads in your signup webhook

```python
from emailkind import EmailKind

client = EmailKind("sk_live_xxx")

def handle_signup(email: str):
    result = client.classify(email=email, enrich=True)
    if result.classification.is_business:
        create_lead(
            email=email,
            company=result.company.name if result.company else None,
            provider=result.provider.name,
            confidence=result.confidence,
        )
        notify_sales(email)
    else:
        start_self_serve_onboarding(email)
```

### Detect Google Workspace vs Gmail accounts

```python
result = client.classify(email="user@company.com")

# Same MX records, but EmailKind distinguishes them
if result.provider.id == "google_workspace":
    print("Paid Google Workspace — likely a real business")
elif result.provider.id == "gmail":
    print("Free Gmail account")
```

### Enrich CRM leads with company names

```python
import csv
from emailkind import EmailKind

client = EmailKind("sk_live_xxx")

with open("leads.csv") as f:
    for row in csv.DictReader(f):
        result = client.classify(email=row["email"], enrich=True)
        if result.company:
            print(f"{row['email']} -> {result.company.name}")
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
    base_url="https://custom.example.com",  # self-hosted or proxy
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
import time
from emailkind import EmailKind

client = EmailKind("sk_live_xxx")

# Upload
job = client.bulk_upload("emails.csv", enrich=True)
print(f"Job {job.id} started")

# Poll until completion
while True:
    status = client.bulk_status(job.id)
    print(f"Progress: {status.processed}/{status.total} ({status.status})")
    if status.status in ("completed", "failed"):
        break
    time.sleep(5)

# Download results
if status.status == "completed":
    csv_bytes = client.bulk_results(job.id)
    with open("results.csv", "wb") as f:
        f.write(csv_bytes)
    print("Results saved to results.csv")
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

### Retry with backoff

```python
import time
from emailkind import EmailKind, RateLimitError

client = EmailKind("sk_live_xxx")

def classify_with_retry(email, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.classify(email=email)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(e.retry_after or (2 ** attempt))
```

## Use with AI agents (MCP)

EmailKind exposes a native [Model Context Protocol](https://modelcontextprotocol.io/) server for Claude Desktop, Cursor, and Windsurf. AI agents can classify emails, detect providers, and enrich company data without writing code.

```json
{
  "mcpServers": {
    "emailkind": {
      "url": "https://emailkind.com/v1/mcp",
      "headers": { "Authorization": "Bearer sk_live_xxx" }
    }
  }
}
```

See [MCP documentation](https://emailkind.com/docs/mcp) for setup instructions.

## Sandbox mode

Use test keys to develop without affecting your quota:

```python
client = EmailKind("sk_test_xxx")
result = client.classify(email="user@gmail.com")
# Works identically, but usage is not tracked
```

## Performance

| Metric | Value |
|--------|-------|
| Response time | < 50ms (p99) |
| Uptime | 99.9% (last 90 days) |
| Providers detected | 150+ |
| Disposable domains | 57,000+ (updated daily) |
| Infrastructure | EU (Germany) |

Rate limits depend on your plan. The SDK raises `RateLimitError` with a `retry_after` value when exceeded.

## Roadmap

- [ ] `AsyncEmailKind` client for asyncio / FastAPI workloads
- [ ] Built-in retry with configurable backoff
- [ ] Webhook signature verification helper

## FAQ

**What's the difference between EmailKind and email verification?**
Email verification pings mailboxes to check if an address exists. EmailKind uses passive DNS analysis to tell you *what kind* of email it is — provider, type, company — without sending anything. Use them together or separately. [Learn more](https://emailkind.com/what-is-email-classification)

**Does EmailKind work with disposable email lists?**
Yes. EmailKind tracks 57,000+ disposable domains, updated daily. The `is_disposable` flag covers all major throwaway services. You can also add your own domains via [custom rules](https://emailkind.com/docs/custom-rules).

**Can I self-host EmailKind?**
Not currently. EmailKind is a hosted API. For enterprise deployments with specific requirements, [contact us](https://emailkind.com/contact).

## Other SDKs

| Language | Package |
|----------|---------|
| Node.js | [`emailkind`](https://www.npmjs.com/package/emailkind) |
| Go | [`emailkind-go`](https://pkg.go.dev/github.com/gastonmedia/emailkind-go) |
| REST | [API docs](https://emailkind.com/docs) |

## Contributing

Bug reports and pull requests are welcome on [GitHub Issues](https://github.com/gastonmedia/emailkind-python/issues).

For bug fixes, feel free to open a PR directly. For new features, please open an issue first to discuss the approach.

## License

[MIT](LICENSE)
