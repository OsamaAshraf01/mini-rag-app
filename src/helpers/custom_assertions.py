from .custom_exceptions import NoneValueException

class AssertExistence:
    def __init__(self, *args):
        for arg in args:
            if arg is None:
                raise NoneValueException
