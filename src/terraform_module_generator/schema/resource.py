"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.base import Schema


class Resource(Schema):
    def __init__(self, name: str, schema: Any) -> None:
        super().__init__(schema)
        self.name = name
