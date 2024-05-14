import re
import functools

from typing import Callable, TypeVar
from typing import Tuple, Type, TypeAlias, Union

# (For type-checkers) To spell out an exception type that could be catched in the try-except block
ExceptionType: TypeAlias = Type[BaseException]
CatchableExceptions: TypeAlias = Union[Tuple[ExceptionType, ...], ExceptionType]


class ArgumentsError(Exception):
    """Represents an error during arguments parsing. 
    
    Shall be thrown when an error has been encountered in the command-line arguments
    """

    def __init__(
        self,
        message: str,
        code: int = 1
    ) -> None:
        """Initializes an ArgumentsError instance"""
        super().__init__(message)
        self.arguments = message
        self.exit_code = code
        return
    
class ForceExit(Exception):
    """Represents a force exit of the program due to some reason. 
    
    This exception shall be thrown if the program encounters an error and could no
    longer continue execution, but can still exit gracefully with a message and exit
    code
    """
    
    def __init__(
        self,
        reason: str,
        original_exception: BaseException = Exception(),
        code: int = 1
    ) -> None:
        """Initializes a ForceExit instance"""
        super().__init__(reason)
        self.exit_code = code
        self.reason = reason
        self.original = original_exception
        return


def exception_name(exception: BaseException) -> str:
    """Returns a clean and human-readable version of the exception by converting the
    camel-case naming convention to regular space-separated words. Mostly for debug
    pretty printing purposes
    """
    return re.sub(r"(?<!^)([A-Z][a-z]+)", r" \1", type(exception).__name__).lower()


def catch(exceptions: CatchableExceptions, message: str, code: int = 1):
    """Run a function with the try and except block, catching any exceptions specified
    in the exceptions parameter. 
    
    If any exceptions are caught, throw a ForceExit exception with the reason specified 
    in the message parameter, and the exit code specified by the parameter code (defaulted
    to 1)
    """
    T = TypeVar("T")
    
    def decorator(func: Callable[..., T]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                ret = func(*args, **kwargs)
            except exceptions as e:
                raise ForceExit(message, original_exception=e, code=code)
            return ret
        return wrapper
    return decorator