"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from terraform_module_generator.schema.blocks import Block


class Schema:
    def __init__(self, schema: Any) -> None:
        self.block = Block(schema.block)
        self.version: int = schema.version
