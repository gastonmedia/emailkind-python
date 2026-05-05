"""EmailKind API client."""

import os

import requests

from .exceptions import (
    AuthenticationError,
    EmailKindError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import BatchResult, BulkJob, ClassifyResult, Rule

__version__ = "0.1.0"

_DEFAULT_BASE_URL = "https://emailkind.com"
_DEFAULT_TIMEOUT = 30


class EmailKind(object):
    """Client for the EmailKind API.

    Args:
        api_key: Your API key (sk_live_xxx or sk_test_xxx).
        base_url: Override the API base URL (default: https://emailkind.com).
        timeout: Request timeout in seconds (default: 30).
    """

    def __init__(self, api_key=None, base_url=None, timeout=None):
        self.api_key = api_key or os.environ.get("EMAILKIND_API_KEY", "")
        if not self.api_key:
            raise AuthenticationError(
                "No API key provided. Pass api_key or set EMAILKIND_API_KEY.",
                code="MISSING_API_KEY",
                status_code=401,
            )
        self.base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else _DEFAULT_TIMEOUT
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": "Bearer {}".format(self.api_key),
                "User-Agent": "emailkind-python/{}".format(__version__),
                "Accept": "application/json",
            }
        )

    # ── Classify ──────────────────────────────────────────────

    def classify(self, email=None, domain=None, enrich=False):
        """Classify a single email or domain.

        Args:
            email: Email address to classify.
            domain: Domain to classify (used if email is not provided).
            enrich: Include company enrichment data.

        Returns:
            ClassifyResult
        """
        params = {}
        if email:
            params["email"] = email
        if domain:
            params["domain"] = domain
        if enrich:
            params["enrich"] = "true"
        data = self._request("GET", "/v1/classify", params=params)
        return ClassifyResult.from_dict(data)

    def classify_batch(self, emails=None, domains=None, enrich=False):
        """Classify multiple emails and/or domains in a single request.

        Args:
            emails: List of email addresses.
            domains: List of domains.
            enrich: Include company enrichment data.

        Returns:
            BatchResult
        """
        body = {}
        if emails:
            body["emails"] = emails
        if domains:
            body["domains"] = domains
        if enrich:
            body["enrich"] = True
        data = self._request("POST", "/v1/classify/batch", json=body)
        return BatchResult.from_dict(data)

    # ── Rules ─────────────────────────────────────────────────

    def list_rules(self):
        """List all custom classification rules.

        Returns:
            list of Rule
        """
        data = self._request("GET", "/v1/rules")
        rules_data = data.get("rules", data) if isinstance(data, dict) else data
        if isinstance(rules_data, list):
            return [Rule.from_dict(r) for r in rules_data]
        return []

    def create_rule(self, match_type, match_value, provider_name, provider_type):
        """Create a custom classification rule.

        Args:
            match_type: Type of match (e.g. "domain", "mx").
            match_value: Value to match against.
            provider_name: Name to assign to matching results.
            provider_type: Type to assign (e.g. "business", "personal").

        Returns:
            Rule
        """
        body = {
            "match_type": match_type,
            "match_value": match_value,
            "provider_name": provider_name,
            "provider_type": provider_type,
        }
        data = self._request("POST", "/v1/rules", json=body)
        return Rule.from_dict(data)

    def delete_rule(self, rule_id):
        """Delete a custom classification rule.

        Args:
            rule_id: ID of the rule to delete.
        """
        self._request("DELETE", "/v1/rules/{}".format(rule_id))

    # ── Bulk ──────────────────────────────────────────────────

    def bulk_upload(self, file, enrich=False):
        """Upload a CSV file for bulk classification.

        Args:
            file: File path (str) or file-like object.
            enrich: Include company enrichment data.

        Returns:
            BulkJob
        """
        opened = False
        if isinstance(file, str):
            fh = open(file, "rb")
            filename = os.path.basename(file)
            opened = True
        else:
            fh = file
            filename = getattr(file, "name", "upload.csv")
            if filename:
                filename = os.path.basename(filename)

        try:
            files = {"file": (filename, fh, "text/csv")}
            form_data = {}
            if enrich:
                form_data["enrich"] = "true"
            data = self._request(
                "POST", "/v1/bulk", files=files, data=form_data
            )
        finally:
            if opened:
                fh.close()

        return BulkJob.from_dict(data)

    def bulk_list(self):
        """List all bulk jobs.

        Returns:
            list of BulkJob
        """
        data = self._request("GET", "/v1/bulk")
        jobs_data = data.get("jobs", data) if isinstance(data, dict) else data
        if isinstance(jobs_data, list):
            return [BulkJob.from_dict(j) for j in jobs_data]
        return []

    def bulk_status(self, job_id):
        """Get the status of a bulk job.

        Args:
            job_id: ID of the bulk job.

        Returns:
            BulkJob
        """
        data = self._request("GET", "/v1/bulk/{}".format(job_id))
        return BulkJob.from_dict(data)

    def bulk_results(self, job_id):
        """Download the results of a completed bulk job as CSV bytes.

        Args:
            job_id: ID of the bulk job.

        Returns:
            bytes: Raw CSV content.
        """
        url = "{}/v1/bulk/{}/results".format(self.base_url, job_id)
        response = self._session.get(url, timeout=self.timeout)
        if response.status_code != 200:
            self._handle_error(response)
        return response.content

    # ── Internal ──────────────────────────────────────────────

    def _request(self, method, path, **kwargs):
        """Make an API request and return parsed JSON.

        Raises:
            EmailKindError or subclass on non-2xx responses.
        """
        url = "{}{}".format(self.base_url, path)
        kwargs.setdefault("timeout", self.timeout)
        response = self._session.request(method, url, **kwargs)

        if response.status_code >= 400:
            self._handle_error(response)

        # DELETE may return empty body
        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    @staticmethod
    def _handle_error(response):
        """Parse an error response and raise the appropriate exception."""
        status = response.status_code
        request_id = None
        code = None
        message = "API request failed with status {}".format(status)

        try:
            data = response.json()
            error = data.get("error", {})
            code = error.get("code", "")
            message = error.get("message", message)
            request_id = data.get("request_id", "")
        except (ValueError, KeyError, AttributeError):
            pass

        kwargs = dict(code=code, request_id=request_id, status_code=status)

        if status == 400:
            raise ValidationError(message, **kwargs)
        elif status == 401:
            raise AuthenticationError(message, **kwargs)
        elif status == 403:
            raise ForbiddenError(message, **kwargs)
        elif status == 404:
            raise NotFoundError(message, **kwargs)
        elif status == 429:
            retry_after = None
            header = response.headers.get("Retry-After")
            if header:
                try:
                    retry_after = int(header)
                except (ValueError, TypeError):
                    pass
            raise RateLimitError(message, retry_after=retry_after, **kwargs)
        else:
            raise EmailKindError(message, **kwargs)
