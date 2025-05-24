#!/usr/bin/env python3
"""Temporary test file to demonstrate MyPy error formatting."""

from typing import List  # This should trigger import error in modern Python
import nonexistent_module  # This will cause import error


def function_without_annotations(x, y):  # Missing type annotations
    """Function missing type annotations."""
    return x + y


def function_with_type_mismatch(name: str) -> int:
    """Function with intentional type mismatch."""
    return name  # Should return int but returns str


def function_with_argument_error() -> None:
    """Function that calls another with wrong argument type."""
    result = function_with_type_mismatch(123)  # Passing int instead of str
    print(result)


class ClassWithErrors:
    """Class with various MyPy errors."""

    def __init__(self, value):  # Missing type annotations
        self.value = value

    def method_with_error(self, data: list[str]) -> str:
        """Method with type error."""
        return data  # Should return str but returns list[str]


# Variable annotation errors
numbers = [1, 2, 3]
result: str = numbers  # Type mismatch


# None handling error
def handle_optional(value: str | None) -> str:
    """Function that doesn't handle None properly."""
    return value.upper()  # Could be None


# Dictionary access error
data: dict[str, int] = {"a": 1, "b": 2}
value: str = data["a"]  # Should be int but assigned to str
