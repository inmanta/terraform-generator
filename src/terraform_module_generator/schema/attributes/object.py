"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import json
import re
from typing import Any, List
from terraform_module_generator.schema.mocks.attribute import AttributeMock

from .base import Attribute, attribute
from .structure import StructureAttribute


def is_object(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        ObjectAttribute.legacy_regex.fullmatch(t) is not None
        or ObjectAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-object-z", condition=is_object)
class ObjectAttribute(StructureAttribute):
    legacy_regex = re.compile(r'\["object",(.+)\]')
    regex = re.compile(r"object\((.+)\)")

    @classmethod
    def get_inner_attributes(cls, schema: Any) -> List[Attribute]:
        raw_inner_attributes_expression = cls.get_inner_attributes_expression(schema)
        inner_attributes_expression: dict = json.loads(raw_inner_attributes_expression)
        return [
            Attribute.build_attribute(
                AttributeMock(
                    type=json.dumps(value).strip().encode("utf-8"),
                    name=key,
                )
            )
            for key, value in inner_attributes_expression.items()
        ]
