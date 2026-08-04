from __future__ import annotations


class ModelProcessingError(RuntimeError):
    """Raised when a schema cannot be converted into a valid generation model."""
