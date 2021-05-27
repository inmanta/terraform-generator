"""
    :copyright: 2021 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import click

from inmanta_module_builder.helpers.const import ASL_2_0_LICENSE, EULA_LICENSE
from inmanta_module_builder.inmanta.module import Module
from inmanta_module_builder.inmanta_module_builder import InmantaModuleBuilder
from terraform_module_generator.terraform_schema_parser import TerraformSchemaParser
from terraform_provider_sdk.terraform_provider_installer import ProviderInstaller
from terraform_provider_sdk.terraform_resource_client import TerraformResourceClient

AVAILABLE_LICENSES = (
    ASL_2_0_LICENSE,
    EULA_LICENSE,
)


def generate_module(
    namespace: str,
    type: str,
    version: str,
    output_dir: str,
    working_dir: str,
    license: Optional[str] = None,
    copyright_header_tmpl: Optional[str] = None,
) -> str:
    installer = ProviderInstaller(namespace, type, version)
    installer.resolve()
    installer.download(working_dir + f"/{namespace}-{type}-{version}")
    installed = installer.install(working_dir, force=True)

    client = TerraformResourceClient(
        installed, working_dir + f"/{namespace}-{type}-{version}.log"
    )
    client.open()
    schema = client.schema
    client.close()

    module = Module(type, version, license=license)
    module_builder = InmantaModuleBuilder(module, Path(output_dir))

    terraform_schema_parser = TerraformSchemaParser(
        module_builder, namespace, type, version, module_name=type
    )
    terraform_schema_parser.parse_module(schema)

    module_builder.generate_module(
        True, copyright_header_template=copyright_header_tmpl
    )


@click.command()
@click.option(
    "--namespace",
    help="The namespace in the terraform registry where the provider relies.",
    required=True,
)
@click.option(
    "--type",
    help="The name of the provider (not the display name).",
    required=True,
)
@click.option(
    "--version",
    help="The version of the provider that should be used for this module generation.",
    required=True,
)
@click.option(
    "--cache-dir",
    help="A directory in which provider binaries should be downloaded an installed, and not cleaned up afterward.",
    required=False,
)
@click.option(
    "--license",
    help=(
        "The copyright to use for the generated module.  You can choose "
        f"between {AVAILABLE_LICENSES}.  Defaults to Inmanta EULA."
    ),
    required=False,
)
@click.option(
    "--copyright-header-from-template-file",
    help="Use the content of the provided file as copyright header.",
    required=False,
)
@click.argument(
    "output_dir",
    required=True,
)
def main(
    namespace: str,
    type: str,
    version: str,
    cache_dir: Optional[str],
    license: Optional[str],
    copyright_header_from_template_file: Optional[str],
    output_dir: str,
) -> None:
    working_dir = cache_dir
    if cache_dir is None:
        working_dir = tempfile.mkdtemp()

    if license is None:
        license = EULA_LICENSE
    if license not in AVAILABLE_LICENSES:
        raise ValueError(
            f"The license should be one of {AVAILABLE_LICENSES} but got {license} instead."
        )

    copyright_header_tmpl = None
    if copyright_header_from_template_file is not None:
        copyright_header_file = Path(copyright_header_from_template_file)
        if not copyright_header_file.exists() or not copyright_header_file.is_file():
            raise ValueError(
                f"The path {copyright_header_from_template_file} doesn't point to a file."
            )

        copyright_header_tmpl = copyright_header_file.read_text()

    generate_module(
        namespace,
        type,
        version,
        output_dir,
        working_dir,
        license,
        copyright_header_tmpl,
    )

    if cache_dir is None:
        shutil.rmtree(working_dir)
