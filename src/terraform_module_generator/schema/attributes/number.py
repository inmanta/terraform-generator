"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.attributes.base import Attribute, attribute


def is_number(attribute: Any) -> bool:
    return attribute.type.decode("utf-8") in ["number", '"number"']


@attribute(index="abc-number-z", condition=is_number)
class NumberAttribute(Attribute):
    pass
