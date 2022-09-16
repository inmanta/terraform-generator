"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, List

from terraform_module_generator.schema.base import Schema


class DataSource(Schema):
    def __init__(self, name: str, path: List[str], schema: Any) -> None:
        super().__init__(name, path, schema)
        self.name = name
