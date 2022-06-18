"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from regex import Pattern

from terraform_module_generator.schema.attributes.base import Attribute


class StructureAttribute(Attribute):
    legacy_regex: Pattern[str]
    regex: Pattern[str]
