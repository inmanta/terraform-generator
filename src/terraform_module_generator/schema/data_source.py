"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, List

from terraform_module_generator.schema.base import Schema
from terraform_module_generator.schema.provider import Provider


class DataSource(Schema):
    def __init__(
        self, name: str, path: List[str], schema: Any, provider: Provider
    ) -> None:
        super().__init__(name, path, schema)
        self.name = name
        self.provider = provider
