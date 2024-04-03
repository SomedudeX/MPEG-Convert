"""Functions and utility classes that does not fit into other files"""
import os
import json
import inspect

from rich.console import Console


class ProgramInfo:
    """Information regarding the program should/will be stored here so that it can be 
    referred to/changed easily
    """

    VERSION = 'v0.2.0'


class Logger:
    """A Logger class that prints to the console"""

    Debug   = 1
    Info    = 2
    Warning = 3
    Fatal   = 4

    def __init__(
        self,
        emit_level: int = 2
    ) -> None:
        """Initiates a Logger class

         + Args - 
            emit_level: All messages greater than or equal to this level (severity) will
            be emitted when calling the logging methods method of this class. """
        self.emit_level = emit_level
        return

    def change_emit_level(
        self,
        new_emit_level: int
    ) -> None:
        """Sets a new emit level; anything above this level will be logged

         + Args -
            new_emit_level: A new emit level that all messages greater than or equal
            to this level (severity) will be emitted when calling the logging methods 
            method of this class. """
        self.emit_level = new_emit_level
        return

    def debug(
        self,
        message: str, 
    ) -> None:
        """Log the specified message to the console with `debug` severity

         + Args -
            message: The message to log to the console
        """
        frame = inspect.stack()[1][0]
        info = inspect.getframeinfo(frame)
        file = info.filename.split("/")
        file = file[len(file) - 1]
        line = info.lineno
        if self.Fatal >= self.emit_level:
            Console().print(f'[grey63]\\[{file}:{line}] [Debug] {message}', highlight=False)
        return

    def info(
        self,
        message: str, 
    ) -> None:
        """Log the specified message to the console with `info` severity

         + Args -
            message: The message to log to the console
        """
        frame = inspect.stack()[1][0]
        info = inspect.getframeinfo(frame)
        file = info.filename.split("/")
        file = file[len(file) - 1]
        line = info.lineno
        if self.Fatal >= self.emit_level:
            Console().print(f'[grey63]\\[{file}:{line}] [white][Info] {message}', highlight=False)
        return

    def warning(
        self,
        message: str, 
    ) -> None:
        """Log the specified message to the console with `warning` severity

         + Args -
            message: The message to log to the console
        """
        frame = inspect.stack()[1][0]
        info = inspect.getframeinfo(frame)
        file = info.filename.split("/")
        file = file[len(file) - 1]
        line = info.lineno
        if self.Fatal >= self.emit_level:
            Console().print(f'[grey63]\\[{file}:{line}] [yellow][Warning] {message}', highlight=False)
        return

    def fatal(
        self,
        message: str, 
    ) -> None:
        """Log the specified message to the console with the `fatal` severity

         + Args -
            message: The message to log to the console
        """
        frame = inspect.stack()[1][0]
        info = inspect.getframeinfo(frame)
        file = info.filename.split("/")
        file = file[len(file) - 1]
        line = info.lineno
        if self.Fatal >= self.emit_level:
            Console().print(f'[grey63]\\[{file}:{line}] [red][Fatal] {message}', highlight=False)
        return


def expand_paths(path: str) -> str:
    """Expand relative paths or paths with tilde (~) to absolute paths"""
    return os.path.normpath(
        os.path.join(
            os.environ['PWD'], 
            os.path.expanduser(path)
        )
    )


def create_json(path: str) -> None:
    """Create a json file if it does not already exist"""
    if not os.path.exists(path):
        file = open(path, 'w')
        json.dump([], file)
        file.close()
    return
