#!/usr/bin/python3
# pylint: disable=missing-module-docstring,redefined-builtin
from builtins import bytes as bbytes
from typing import TypeVar, Type, Any

_T = TypeVar("_T")


class bytes(bbytes):
    """Local override of builtin bytes class to add "lazy_decode"

    bytes(iterable_of_ints) -> bytes
    bytes(string, encoding[, errors]) -> bytes
    bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
    bytes(int) -> bytes object of size given by the parameter initialized with null bytes
    bytes() -> empty bytes object

    Construct an immutable array of bytes from:
      - an iterable yielding integers in range(256)
      - a text string encoded using the specified encoding
      - any object implementing the buffer API.
      - an integer
    """

    def __new__(
        cls: Type[_T],
        thing: Any = None,
        encoding: str = "UTF-8",
        errors: str = "strict",
    ) -> _T:
        if isinstance(thing, str):
            cls.value = super().__new__(cls, thing, encoding, errors)  # type: ignore
        elif thing is None:
            cls.value = super().__new__(cls)  # type: ignore
        elif thing is not None:
            cls.value = super().__new__(cls, thing)  # type: ignore
        else:
            raise AttributeError("This shouldn't happen")
        return cls.value  # type: ignore

    @classmethod
    def lazy_decode(cls) -> str:
        "Lazily decode the bytes object using string manipulation"
        return str(cls.value)[2:-1]

    @classmethod
    def safe_decode(cls) -> str:
        'Calls cls.decode(cls, errors = "ignore"), if that errors, returns "nul"'
        try:
            return cls.decode(cls.value, errors="ignore")  # type: ignore
        except TypeError:
            print("panik - invalid UTF-8")
            return "nul"
