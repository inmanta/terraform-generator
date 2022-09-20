"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import json
import re
import typing

from inmanta_module_factory import builder, inmanta

from terraform_module_generator.schema.mocks.attribute import AttributeMock

from .base import Attribute, attribute
from .structure import StructureAttribute


def is_tuple(attribute: typing.Any) -> bool:
    t = attribute.type.decode("utf-8")
    return (
        TupleAttribute.legacy_regex.fullmatch(t) is not None
        or TupleAttribute.regex.fullmatch(t) is not None
    )


@attribute(index="abc-tuple-z", condition=is_tuple)
class TupleAttribute(StructureAttribute):
    legacy_regex = re.compile(r'\["tuple",(.+)\]')
    regex = re.compile(r"tuple\((.+)\)")

    def inmanta_attribute_type(
        self, module_builder: builder.InmantaModuleBuilder
    ) -> inmanta.InmantaType:
        raise NotImplementedError("This should be replaced by a real entity")

    @classmethod
    def get_inner_attributes(
        cls, path: typing.List[str], schema: typing.Any
    ) -> typing.List[Attribute]:
        raw_inner_attributes_expression = cls.get_inner_attributes_expression(schema)
        inner_attributes_expression: list = json.loads(raw_inner_attributes_expression)
        return [
            Attribute.build_attribute(
                path,
                AttributeMock(
                    name=f"attr{i}",
                    type=json.dumps(value).strip().encode("utf-8"),
                ),
            )
            for i, value in enumerate(inner_attributes_expression)
        ]
