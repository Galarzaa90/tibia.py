class TibiapyException(Exception):
    """
    Base exception for the tibiapy module.

    All exceptions thrown by the module are inherited from this.
    """
    pass


class InvalidContent(TibiapyException):
    """Exception thrown when the provided content is unrelated for the calling function.

    This usually means that the content provided belongs to a different website or section of the website.
    This serves as a way to differentiate those cases from a parsing that returned no results (e.g. Character not found)

    In some cases this can mean that Tibia.com's format has changed and the library needs updating.

    Attributes
    ----------
    original: :class:`Exception`
        The original exception that caused this exception."""
    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


class NetworkError(TibiapyException):
    """Exception thrown when there was a network error trying to fetch a resource from the web.

    Attributes
    ----------
    original: :class:`Exception`
        The original exception that caused this exception."""
    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


class Forbidden(NetworkError):
    """A subclass of network error thrown when Tibia.com returns a 403 status code.

    Tibia.com returns a 403 status code when it detects that too many requests are being done.
    This has its own subclass to let the user decide to treat this differently than other network errors.
    """
