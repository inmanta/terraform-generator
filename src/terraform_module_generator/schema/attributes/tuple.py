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


def is_tuple(attribute: Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        TupleAttribute.legacy_regex.fullmatch(t) is not None
        or TupleAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-tuple-z", condition=is_tuple)
class TupleAttribute(StructureAttribute):
    legacy_regex = re.compile(r'\["tuple",(.+)\]')
    regex = re.compile(r"tuple\((.+)\)")

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
        inner_attributes_expression: list = json.loads(raw_inner_attributes_expression)
        return [
            Attribute.build_attribute(
                AttributeMock(
                    type=json.dumps(value).strip().encode("utf-8"),
                )
            )
            for value in inner_attributes_expression
        ]
