"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any, List

from terraform_module_generator.schema.blocks import Block


class Schema:
    def __init__(self, name: str, path: List[str], schema: Any) -> None:
        self.block = Block(name, path, schema.block)
        self.version: int = schema.version
