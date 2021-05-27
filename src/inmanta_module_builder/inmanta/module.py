"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import datetime
from typing import Optional

from inmanta_module_builder.helpers.const import (
    ASL_2_0_COPYRIGHT_HEADER_TMPL,
    ASL_2_0_LICENSE,
    EULA_COPYRIGHT_HEADER_TMPL,
    EULA_LICENSE,
)


class Module:
    def __init__(
        self,
        name: str,
        version: str = "0.0.1",
        description: Optional[str] = None,
        author: str = "Inmanta",
        author_email: str = "code@inmanta.com",
        license: str = ASL_2_0_LICENSE,
        copyright: str = f"{datetime.datetime.now().year} Inmanta",
        compiler_version: Optional[str] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.description = description or ""
        self.author = author
        self.author_email = author_email
        self.license = license
        self.copyright = copyright
        self.compiler_version = compiler_version

    def file_header(self, template: Optional[str] = None) -> str:
        tmpl_dict = {
            "copyright": self.copyright,
            "contact": self.author_email,
            "author": self.author,
        }
        if template is not None:
            return template % tmpl_dict
        if self.license == ASL_2_0_LICENSE:
            return ASL_2_0_COPYRIGHT_HEADER_TMPL % tmpl_dict
        if self.license == EULA_LICENSE:
            return EULA_COPYRIGHT_HEADER_TMPL % tmpl_dict

        return ""

    def as_dict(self) -> dict:
        module_config = dict(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            author_email=self.author_email,
            license=self.license,
            copyright=self.copyright,
        )
        if self.compiler_version is not None:
            module_config["compiler_version"] = self.compiler_version
        return module_config
