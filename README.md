# Terraform module generator

The terraform module generator can be used to build inmanta modules from a terraform provider.  It will download the provider binary, execute it and get the schema from it.  Then parse this schema and generate a python representation of the inmanta module, that will then be consumed by the inmanta module builder to generate the proper module.

## Usage
In order to generate a module, you will need to provide the following information:
 - `namespace`: The namespace in the terraform registry where the provider relies.
 - `type`: The name of the provider (not the display name).
 - `version`: The version of the provider that should be used for this module generation.

### Using the CLI

```console
$ python src/__init__.py --help
Usage: __init__.py [OPTIONS] OUTPUT_DIR

Options:
  --namespace TEXT                The namespace in the terraform registry
                                  where the provider relies.  [required]
  --type TEXT                     The name of the provider (not the display
                                  name).  [required]
  --version TEXT                  The version of the provider that should be
                                  used for this module generation.  [required]
  --cache-dir TEXT                A directory in which provider binaries
                                  should be downloaded an installed, and not
                                  cleaned up afterward.
  --license TEXT                  The copyright to use for the generated
                                  module.  You can choose between ('ASL 2.0',
                                  'Inmanta EULA').  Defaults to Inmanta EULA.
  --copyright-header-from-template-file TEXT
                                  Use the content of the provided file as
                                  copyright header.
  --v1                            Generate a v1 module, generate a v2 module
                                  if not set
  --help                          Show this message and exit.
$ python src/__init__.py --namespace hashicorp --type local --version 2.1.0 --cache-dir /tmp/cache /tmp
```

The `--copyright-header-from-template-file` argument takes a path to file containing a template of this form:
```
"""
My own header for this copyright: %(copyright)s
By %(author)s (%(contact)s)
"""
```

### With Python

```python
from pathlib import Path

from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_plugins.terraform.tf.terraform_provider import TerraformProvider
from inmanta_plugins.terraform.tf.terraform_provider_installer import ProviderInstaller

from terraform_module_generator.terraform_schema_parser import TerraformSchemaParser

DOWNLOAD_PATH = "/tmp/terraform-providers/download"
INSTALL_PATH = "/tmp/terraform-providers/install"
LOGGING_PATH = "/tmp/terraform-providers/logs"

OUTPUT_PATH = os.getcwd()

Path(DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
Path(INSTALL_PATH).mkdir(parents=True, exist_ok=True)
Path(LOGGING_PATH).mkdir(parents=True, exist_ok=True)


def generate_model(namespace: str, type: str, version: str) -> str:
    installer = ProviderInstaller(namespace, type, version)
    installer.resolve()
    installer.download(DOWNLOAD_PATH + f"/{namespace}-{type}-{version}")
    installed = installer.install(INSTALL_PATH, force=True)

    with TerraformProvider(
        installed, LOGGING_PATH + f"/{namespace}-{type}-{version}.log"
    ) as provider:
        provider_schema = provider.schema

    module = Module(type, version)
    module_builder = InmantaModuleBuilder(
        module,
        generation="v1" if v1 else "v2",
    )

    terraform_module = schema.Module(
        name=type,
        schema=provider_schema,
        namespace=namespace,
        type=type,
        version=version,
    )
    terraform_module.build(module_builder)

    return module_builder.generate_module(Path(OUTPUT_PATH), True).path


generate_model("hashicorp", "local", "2.1.0")
```

### Tested modules
| **Namespace** | **Type** | **Version** |
| --- | --- | --- |
| `hashicorp` | `local` | `2.1.0` |
| `fortinetdev` | `fortios` | `1.11.0` |
| `CheckpointSW` | `checkpoint` | `1.4.0` |
| `gitlabhq` | `gitlab` | `3.6.0` |
| `integrations` | `github` | `4.10.1` |
| `kreuzwerker` | `docker` | `2.22.0` |


## License

This module is available as opensource under ASL2 and commercially under the Inmanta EULA, with the following disclaimer:

This package is an Inmanta internal tool, with no other purpose than assisting in the construction of specific modules.
This package provides no functionality of its own, has no implied warranties and has no fitness for any particular purpose.
It requires specific training to use safely.

No support is provided on this module except through Inmanta supported and licensed modules that use its functionality
