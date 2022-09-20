"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from typing import Any

from .data_source import DataSource
from .provider import Provider
from .resource import Resource


class Module:
    def __init__(self, name: str, schema: Any) -> None:
        self.name = name
        self.provider = Provider("provider", [name], schema.provider)
        self.resources = [
            Resource(key, [name, "resources"], s)
            for key, s in schema.resource_schemas.items()
        ]
        self.data_sources = [
            DataSource(key, [name, "data_sources"], d)
            for key, d in schema.data_source_schemas.items()
        ]
