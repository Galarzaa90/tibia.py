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

    In some cases this can mean that Tibia.com's format has changed and the library needs updating."""
    pass
