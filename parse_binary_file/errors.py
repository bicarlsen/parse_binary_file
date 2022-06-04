class AlreadyLoaded(Exception):
    """
    Raised when data is already loaded
    """
    pass


class ValuesDoNotMatch(Exception):
    """
    Raised when the given field value and the expected value do not match.
    """
    pass
