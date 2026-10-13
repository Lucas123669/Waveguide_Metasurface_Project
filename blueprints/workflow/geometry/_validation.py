"""Small strict-validation helpers for standalone geometry mappings."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def require_mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise TypeError(f"{path} keys must be strings")
    return value


def require_exact_keys(
    value: Mapping[str, object],
    path: str,
    required: set[str],
) -> None:
    missing = sorted(required.difference(value))
    if missing:
        raise ValueError(f"{path} is missing required fields: {', '.join(missing)}")
    unknown = sorted(set(value).difference(required))
    if unknown:
        raise ValueError(f"{path} contains unknown fields: {', '.join(unknown)}")


def require_number(
    value: object,
    path: str,
    *,
    positive: bool = False,
    non_negative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{path} must be finite")
    if positive and result <= 0.0:
        raise ValueError(f"{path} must be positive")
    if non_negative and result < 0.0:
        raise ValueError(f"{path} must be non-negative")
    return result


def require_integer(
    value: object,
    path: str,
    *,
    positive: bool = False,
) -> int:
    if type(value) is not int:
        raise TypeError(f"{path} must be an integer")
    result = int(value)
    if positive and result <= 0:
        raise ValueError(f"{path} must be positive")
    return result


def require_vector2(value: object, path: str) -> tuple[float, float]:
    if (
        isinstance(value, (str, bytes))
        or not isinstance(value, Sequence)
        or len(value) != 2
    ):
        raise TypeError(f"{path} must be a two-number array")
    return (
        require_number(value[0], f"{path}[0]"),
        require_number(value[1], f"{path}[1]"),
    )
