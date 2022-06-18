"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import re
from typing import Any

from .base import attribute
from .collection import CollectionAttribute


def is_set(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        SetAttribute.legacy_regex.fullmatch(t) is not None
        or SetAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-set-z", condition=is_set)
class SetAttribute(CollectionAttribute):
    legacy_regex = re.compile(r'\["set",(.+)\]')
    regex = re.compile(r"set\((.+)\)")
