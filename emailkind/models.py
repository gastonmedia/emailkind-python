"""Data models for the EmailKind SDK."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Provider(object):
    """Email provider information."""

    id = ""  # type: str
    name = ""  # type: str
    type = ""  # type: str

    def __init__(self, id="", name="", type=""):
        self.id = id
        self.name = name
        self.type = type

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> Provider
        if data is None:
            return cls()
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
        )


@dataclass
class Classification(object):
    """Email classification flags."""

    is_business = False  # type: bool
    is_free = False  # type: bool
    is_disposable = False  # type: bool
    is_education = False  # type: bool
    is_custom_domain = False  # type: bool
    is_role = False  # type: bool

    def __init__(
        self,
        is_business=False,
        is_free=False,
        is_disposable=False,
        is_education=False,
        is_custom_domain=False,
        is_role=False,
    ):
        self.is_business = is_business
        self.is_free = is_free
        self.is_disposable = is_disposable
        self.is_education = is_education
        self.is_custom_domain = is_custom_domain
        self.is_role = is_role

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> Classification
        if data is None:
            return cls()
        return cls(
            is_business=data.get("is_business", False),
            is_free=data.get("is_free", False),
            is_disposable=data.get("is_disposable", False),
            is_education=data.get("is_education", False),
            is_custom_domain=data.get("is_custom_domain", False),
            is_role=data.get("is_role", False),
        )


@dataclass
class Company(object):
    """Enrichment company data (only present when enrich=true)."""

    name = ""  # type: str
    source = ""  # type: str
    has_favicon = False  # type: bool

    def __init__(self, name="", source="", has_favicon=False):
        self.name = name
        self.source = source
        self.has_favicon = has_favicon

    @classmethod
    def from_dict(cls, data):
        # type: (Optional[dict]) -> Optional[Company]
        if data is None:
            return None
        return cls(
            name=data.get("name", ""),
            source=data.get("source", ""),
            has_favicon=data.get("has_favicon", False),
        )


@dataclass
class ClassifyResult(object):
    """Result from a single classify request."""

    success = True  # type: bool
    request_id = ""  # type: str
    email = ""  # type: str
    normalized_email = ""  # type: str
    domain = ""  # type: str
    provider = None  # type: Optional[Provider]
    classification = None  # type: Optional[Classification]
    mx = None  # type: Optional[List[str]]
    confidence = 0.0  # type: float
    cached = False  # type: bool
    company = None  # type: Optional[Company]

    def __init__(
        self,
        success=True,
        request_id="",
        email="",
        normalized_email="",
        domain="",
        provider=None,
        classification=None,
        mx=None,
        confidence=0.0,
        cached=False,
        company=None,
    ):
        self.success = success
        self.request_id = request_id
        self.email = email
        self.normalized_email = normalized_email
        self.domain = domain
        self.provider = provider
        self.classification = classification
        self.mx = mx if mx is not None else []
        self.confidence = confidence
        self.cached = cached
        self.company = company

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> ClassifyResult
        return cls(
            success=data.get("success", True),
            request_id=data.get("request_id", ""),
            email=data.get("email", ""),
            normalized_email=data.get("normalized_email", ""),
            domain=data.get("domain", ""),
            provider=Provider.from_dict(data.get("provider")),
            classification=Classification.from_dict(data.get("classification")),
            mx=data.get("mx", []),
            confidence=data.get("confidence", 0.0),
            cached=data.get("cached", False),
            company=Company.from_dict(data.get("company")),
        )


@dataclass
class BatchResultItem(object):
    """A single item within a batch classify response."""

    input = ""  # type: str
    success = True  # type: bool
    domain = ""  # type: str
    normalized_email = ""  # type: str
    provider = None  # type: Optional[Provider]
    classification = None  # type: Optional[Classification]
    confidence = 0.0  # type: float
    company = None  # type: Optional[Company]
    error = None  # type: Optional[dict]

    def __init__(
        self,
        input="",
        success=True,
        domain="",
        normalized_email="",
        provider=None,
        classification=None,
        confidence=0.0,
        company=None,
        error=None,
    ):
        self.input = input
        self.success = success
        self.domain = domain
        self.normalized_email = normalized_email
        self.provider = provider
        self.classification = classification
        self.confidence = confidence
        self.company = company
        self.error = error

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> BatchResultItem
        return cls(
            input=data.get("input", ""),
            success=data.get("success", True),
            domain=data.get("domain", ""),
            normalized_email=data.get("normalized_email", ""),
            provider=Provider.from_dict(data.get("provider")),
            classification=Classification.from_dict(data.get("classification")),
            confidence=data.get("confidence", 0.0),
            company=Company.from_dict(data.get("company")),
            error=data.get("error"),
        )


@dataclass
class BatchResult(object):
    """Result from a batch classify request."""

    success = True  # type: bool
    request_id = ""  # type: str
    count = 0  # type: int
    results = None  # type: Optional[List[BatchResultItem]]

    def __init__(self, success=True, request_id="", count=0, results=None):
        self.success = success
        self.request_id = request_id
        self.count = count
        self.results = results if results is not None else []

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> BatchResult
        results_data = data.get("results", [])
        return cls(
            success=data.get("success", True),
            request_id=data.get("request_id", ""),
            count=data.get("count", 0),
            results=[BatchResultItem.from_dict(r) for r in results_data],
        )


@dataclass
class Rule(object):
    """A custom classification rule."""

    id = ""  # type: str
    match_type = ""  # type: str
    match_value = ""  # type: str
    provider_name = ""  # type: str
    provider_type = ""  # type: str
    created_at = ""  # type: str

    def __init__(
        self,
        id="",
        match_type="",
        match_value="",
        provider_name="",
        provider_type="",
        created_at="",
    ):
        self.id = id
        self.match_type = match_type
        self.match_value = match_value
        self.provider_name = provider_name
        self.provider_type = provider_type
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> Rule
        return cls(
            id=data.get("id", ""),
            match_type=data.get("match_type", ""),
            match_value=data.get("match_value", ""),
            provider_name=data.get("provider_name", ""),
            provider_type=data.get("provider_type", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class BulkJob(object):
    """A bulk processing job."""

    id = ""  # type: str
    status = ""  # type: str
    total = 0  # type: int
    processed = 0  # type: int
    created_at = ""  # type: str
    completed_at = ""  # type: str
    filename = ""  # type: str
    error = ""  # type: str

    def __init__(
        self,
        id="",
        status="",
        total=0,
        processed=0,
        created_at="",
        completed_at="",
        filename="",
        error="",
    ):
        self.id = id
        self.status = status
        self.total = total
        self.processed = processed
        self.created_at = created_at
        self.completed_at = completed_at
        self.filename = filename
        self.error = error

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> BulkJob
        return cls(
            id=data.get("id", ""),
            status=data.get("status", ""),
            total=data.get("total", 0),
            processed=data.get("processed", 0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at", ""),
            filename=data.get("filename", ""),
            error=data.get("error", ""),
        )
