"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.attributes.base import Attribute, attribute


def is_string(attribute: Any) -> bool:
    return attribute.type.decode("utf-8") in ["string", '"string"']


@attribute(index="abc-string-z", condition=is_string)
class StringAttribute(Attribute):
    pass
