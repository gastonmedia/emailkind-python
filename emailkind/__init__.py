"""EmailKind Python SDK — classify email addresses by provider and type."""

from .client import EmailKind, __version__
from .exceptions import (
    AuthenticationError,
    EmailKindError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import (
    BatchResult,
    BatchResultItem,
    BulkJob,
    Classification,
    ClassifyResult,
    Company,
    Provider,
    Rule,
)

__all__ = [
    "EmailKind",
    "__version__",
    # Exceptions
    "EmailKindError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ForbiddenError",
    "NotFoundError",
    # Models
    "ClassifyResult",
    "BatchResult",
    "BatchResultItem",
    "Provider",
    "Classification",
    "Company",
    "Rule",
    "BulkJob",
]
