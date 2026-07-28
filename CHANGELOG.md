# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-07-28

### Added

- `Classification.is_role` — role-based address detection (e.g. `info@`, `support@`)
- `normalized_email` on `ClassifyResult` and batch result items — alias-normalized form of the input
- `Company.has_favicon` — active-website signal on enrichment results

## [0.1.0] - 2025-05-01

### Added

- `EmailKind` client with API key and environment variable configuration
- `classify()` — single email/domain classification with optional company enrichment
- `classify_batch()` — batch classification of up to 100 emails/domains
- `list_rules()`, `create_rule()`, `delete_rule()` — custom classification rules
- `bulk_upload()`, `bulk_status()`, `bulk_results()`, `bulk_list()` — async CSV processing
- Typed exceptions: `AuthenticationError`, `RateLimitError`, `ValidationError`, `ForbiddenError`, `NotFoundError`
- Sandbox mode with `sk_test_*` keys
- Structured data models: `ClassifyResult`, `Provider`, `Classification`, `Company`, `BatchResult`, `Rule`, `BulkJob`

[0.2.0]: https://github.com/gastonmedia/emailkind-python/releases/tag/v0.2.0
[0.1.0]: https://github.com/gastonmedia/emailkind-python/releases/tag/v0.1.0
