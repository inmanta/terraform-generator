"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from dataclasses import dataclass


@dataclass()
class AttributeMock:
    """
    Mock object for https://github.com/inmanta/inmanta-tfplugin/blob
        /7269bc7d28d751b5dc110161dae29a6209c3fb63/docs/tf_grpc_plugin
        /proto/inmanta_tfplugin/tfplugin5.proto#L90
    """

    name: str
    type: bytes
    description: str = ""
    required: bool = False
    optional: bool = False
    computed: bool = False
    sensitive: bool = False
    description_kind: str = ""
    deprecated: bool = False
