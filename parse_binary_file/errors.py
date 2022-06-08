"""
Custom exceptions.
"""


class IncompatibleProperties(ValueError):
    """
    Raised when two proeprties are incompatible.

    :param msg: Message to display.
    :param p1: First property.
    :param p2: Second proprty.
    """
    def __init__(self, msg=None, p1=None, p2=None):
        super().__init__(msg)
        self.properties = (p1, p2)


class ValuesDoNotMatch(ValueError):
    """
    Raised when the given field value and the expected value do not match.
    """
