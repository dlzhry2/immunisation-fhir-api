"""Custom exceptions for the Ack lambda."""


class UnhandledAuditTableError(Exception):
    """A custom exception for when an unexpected error occurs whilst adding the file to the audit table."""
