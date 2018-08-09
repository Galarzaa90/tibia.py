class TibiapyException(Exception):
    """
    Base exception for the tibiapy module.

    All exceptions thrown by the module are inherited from this.
    """
    pass


class InvalidContent(TibiapyException):
    """Exception thrown when the parsing couldn't be completed due to invalid content supplied.

    This usually means that the content provided belongs to a different website or section.

    In some cases this can mean that Tibia.com's format has changed and the library needs updating."""
    pass
