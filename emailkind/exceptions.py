"""Exception classes for the EmailKind SDK."""


class EmailKindError(Exception):
    """Base exception for all EmailKind API errors."""

    def __init__(self, message, code=None, request_id=None, status_code=None):
        self.message = message
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        parts = []
        if self.code:
            parts.append("[{}]".format(self.code))
        parts.append(self.message)
        if self.request_id:
            parts.append("(request_id: {})".format(self.request_id))
        return " ".join(parts)


class AuthenticationError(EmailKindError):
    """Raised when the API key is invalid or missing (HTTP 401)."""

    def __init__(self, message="Invalid or missing API key", **kwargs):
        super().__init__(message, **kwargs)


class ForbiddenError(EmailKindError):
    """Raised when the API key lacks permission for the requested action (HTTP 403)."""

    def __init__(self, message="Forbidden", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(EmailKindError):
    """Raised when the request parameters are invalid (HTTP 400)."""

    def __init__(self, message="Invalid request parameters", **kwargs):
        super().__init__(message, **kwargs)


class NotFoundError(EmailKindError):
    """Raised when the requested resource is not found (HTTP 404)."""

    def __init__(self, message="Resource not found", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitError(EmailKindError):
    """Raised when the rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Number of seconds to wait before retrying.
    """

    def __init__(self, message="Rate limit exceeded", retry_after=None, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, **kwargs)

    def __str__(self):
        base = super().__str__()
        if self.retry_after is not None:
            return "{} (retry after {}s)".format(base, self.retry_after)
        return base
