"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.attributes.base import Attribute, attribute


def is_bool(attribute: Any) -> bool:
    return attribute.type.decode("utf-8") in ["bool", '"bool"']


@attribute(index="abc-boolean-z", condition=is_bool)
class BooleanAttribute(Attribute):
    pass
