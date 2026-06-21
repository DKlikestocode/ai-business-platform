"""Domain-level exceptions."""


class DomainError(Exception):
    """Base exception for domain errors."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class ConflictError(DomainError):
    """Raised when a create/update violates a uniqueness constraint."""


class AuthenticationError(DomainError):
    """Raised when credentials are invalid or the account cannot authenticate."""


class NotificationDeliveryError(DomainError):
    """Raised when an outbound notification could not be delivered."""


class InvalidWidgetHeartbeatError(DomainError):
    """Raised when widget heartbeat credentials or origin are invalid."""
