"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


def cache_method_result(func: F) -> F:
    """
    Decorator for objects methods.  When added to a method, the method body
    will only be called once, and the response object will be attached to the
    object.  If the method is called a second time, the result is taken from
    the value stored on the object.
    """
    func_name = func.__name__
    func_result_attribute = f"__{func_name}_result"

    def cache(self, *args, **kwargs) -> object:
        if not hasattr(self, func_result_attribute):
            setattr(self, func_result_attribute, func(self, *args, **kwargs))

        return getattr(self, func_result_attribute)

    return cache
