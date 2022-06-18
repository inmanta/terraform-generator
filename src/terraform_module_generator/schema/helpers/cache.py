from typing import Any, Callable, Dict, TypeVar


F = TypeVar("F", bound=Callable)


def cache(func: F) -> F:
    """
    Cache the response of the function and returns it for all the next
    calls to the function.  This doesn't take into account the arguments
    that are given to the function except for the first one, which is
    expected to be 'self'.  No matter what, the method of the object will
    be called at most once.
    """
    res: Dict[Any, Any] = {}
    def cache_or_call(self, *args, **kwargs) -> Any:
        if self not in res:
            res[self] = func(self, *args, **kwargs)
        
        return res[self]
    
    return cache_or_call
