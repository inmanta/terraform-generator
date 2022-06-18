"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import json
import re
from typing import Any, Dict

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

    def __init__(self, schema: Any) -> None:
        super().__init__(schema)
        self.inner_attributes = self.get_inner_attributes(schema)

    @classmethod
    def get_inner_attributes_expression(cls, schema: Any) -> str:
        t = schema.type.decode("utf-8")
        legacy_match = cls.legacy_regex.fullmatch(t)
        if legacy_match:
            return legacy_match.group(1)

        match = cls.regex.fullmatch(t)
        if match:
            return match.group(1)

        raise ValueError(f"Failed to match type: {t}")

    @classmethod
    def get_inner_attributes(cls, schema: Any) -> Dict[str, Attribute]:
        raw_inner_attributes_expression = cls.get_inner_attributes_expression(schema)
        inner_attributes_expression: dict = json.loads(raw_inner_attributes_expression)
        return {
            key: Attribute.build_attribute(
                AttributeMock(
                    type=json.dumps(value).strip().encode("utf-8"),
                )
            )
            for key, value in inner_attributes_expression.items()
        }
