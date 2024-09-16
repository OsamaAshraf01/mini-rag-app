from .custom_exceptions import NoneValueException

def execution_manager(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoneValueException:
            return None
        
    return inner
