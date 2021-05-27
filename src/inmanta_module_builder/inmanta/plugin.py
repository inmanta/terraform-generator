"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from textwrap import indent
from typing import List, Optional, Set, Union

from inmanta_module_builder.helpers.const import INDENT_PREFIX
from inmanta_module_builder.inmanta.entity import Entity


class PluginArgument:
    def __init__(
        self,
        name: str,
        inmanta_type: Union[Entity, str],
        description: Optional[str] = None,
    ) -> None:
        self.name = name
        self.inmanta_type = inmanta_type
        self.description = description

    def __str__(self) -> str:
        type_expression = self.inmanta_type
        if isinstance(self.inmanta_type, Entity):
            type_expression = self.inmanta_type.full_path_string

        return f'{self.name}: "{type_expression}"'


class Plugin:
    def __init__(
        self,
        name: str,
        arguments: List[PluginArgument],
        return_type: PluginArgument,
        content: str,
        description: Optional[str] = None,
    ) -> None:
        """
        A plugin to add in the plugins/__init__.py file of the module.
        :param name: The name of the plugin definition
        :param arguments: A list of arguments that the plugin takes
        :param return_type: The return type of the plugin
        :param content: The content (python statements) of the plugin
        :param description: A description of the plugin, to be added as docstring
        """
        self.name = name
        self.arguments = arguments
        self.return_type = return_type
        self.content = content
        self.description = description
        self.imports = {"from inmanta.plugins import plugin"}

    def get_imports(self) -> Set[str]:
        return self.imports

    def add_import(self, import_value: str) -> None:
        self.imports.add(import_value)

    def docstring(self) -> str:
        doc = "This docstring has been automatically generated.\n"
        if self.description:
            doc += self.description + "\n"

        for argument in self.arguments:
            description = argument.description or ""
            doc += f":param {argument.name}: {description}\n"

        if self.return_type.description:
            doc += f":return: {self.return_type.description}\n"

        return doc

    def __str__(self) -> str:
        return (
            "@plugin\n"
            + f'def {self.name}({", ".join([str(arg) for arg in self.arguments])}) -> "{self.return_type.inmanta_type}":\n'
            + indent(
                ('"""\n' + self.docstring() + '"""\n' + self.content),
                prefix=INDENT_PREFIX,
            )
            + "\n"
        )
