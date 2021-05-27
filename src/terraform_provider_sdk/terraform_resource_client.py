"""
    Copyright 2021 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import datetime
import subprocess
import threading
from typing import IO, Any, List

import grpc
import tfplugin5.tfplugin5_pb2 as tfplugin5_pb2
import tfplugin5.tfplugin5_pb2_grpc as tfplugin5_pb2_grpc

from terraform_provider_sdk.exceptions import PluginInitException

MAGIC_NAME = "TF_PLUGIN_MAGIC_COOKIE"
MAGIC_VALUE = "d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2"
CORE_PROTOCOL_VERSION = 1
SUPPORTED_VERSIONS = (4, 5)
TERRAFORM_VERSION = "0.14.10"


def format_log_line(line: str, prefixes: List[str], show_time: bool = True) -> str:
    prefix = "[" + "][".join(prefixes) + "]"
    if show_time:
        prefix = f"[{str(datetime.datetime.now())}] {prefix}"

    return f"{prefix}: {line.strip()}\n"


class TerraformResourceClient:
    def __init__(
        self,
        provider_path: str,
        log_file_path: str,
    ) -> None:
        self._provider_path: str = provider_path
        self._log_file_path: str = log_file_path
        self._proc: subprocess.Popen = None
        self._stub: tfplugin5_pb2_grpc.ProviderStub = None
        self._stdout_thread: threading.Thread = None
        self._stderr_thread: threading.Thread = None
        self._schema = None

    def _io_logger(self, stream: IO[bytes], prefixes: List[str]) -> None:
        while self._proc:
            line = stream.readline().decode().strip()
            if not line:
                continue

            with open(self._log_file_path, "a") as f:
                f.write(format_log_line(line, prefixes))

    def _parse_proto(self, line: str) -> str:
        parts = line.split("|")
        if len(parts) < 4:
            raise PluginInitException(f"Invalid protocol response of plugin: '{line}'")

        core_version = int(parts[0])
        if core_version != CORE_PROTOCOL_VERSION:
            raise PluginInitException(
                f"Invalid core protocol version: '{core_version}' (expected {CORE_PROTOCOL_VERSION})"
            )

        proto_version = int(parts[1])
        if proto_version not in SUPPORTED_VERSIONS:
            raise PluginInitException(
                "Invalid protocol version for plugin %d. Only %s supported.",
                proto_version,
                SUPPORTED_VERSIONS,
            )

        proto_type = parts[2]
        if proto_type != "unix":
            raise PluginInitException(
                f"Only unix sockets are supported, but got '{proto_type}'"
            )

        proto = parts[4]
        if proto != "grpc":
            raise PluginInitException(
                f"Only GRPC protocol is supported, but got '{proto}'"
            )

        return f"{proto_type}://{parts[3]}"

    def open(self) -> None:
        """
        This methods has to be called once for each provider
        It will create a new process and execute the provider binary in it.
        We then create a stub, to communicate via grpc with the provider.
        End finally we apply to the running provider the provided configuration.

        :param provider_config: The config to apply to the provider.  Missing values will
            be set to None automatically.
        """
        if self._proc:
            return

        self._proc = subprocess.Popen(
            self._provider_path,
            env={
                MAGIC_NAME: MAGIC_VALUE,
                "PLUGIN_MIN_PORT": "40000",
                "PLUGIN_MAX_PORT": "41000",
                "PLUGIN_PROTOCOL_VERSIONS": ",".join(
                    [str(v) for v in SUPPORTED_VERSIONS]
                ),
                "TF_LOG": "TRACE",
                "TF_LOG_LEVEL": "DEBUG",
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        with open(self._log_file_path, "a") as f:
            f.write(
                format_log_line(
                    f"Started plugin with pid {self._proc.pid}", ["HANDLER", "DEBUG"]
                )
            )

        line = self._proc.stdout.readline().decode().strip()
        proto_addr = self._parse_proto(line)

        self._stdout_thread = threading.Thread(
            target=self._io_logger, args=(self._proc.stdout, ["PROVIDER", "STDOUT"])
        )
        self._stdout_thread.start()

        self._stderr_thread = threading.Thread(
            target=self._io_logger, args=(self._proc.stderr, ["PROVIDER", "STDERR"])
        )
        self._stderr_thread.start()

        channel = grpc.insecure_channel(proto_addr)
        self._stub = tfplugin5_pb2_grpc.ProviderStub(channel)

    def close(self) -> None:
        """
        This method has to be called once for each provider, once we are done with it.
        It will close the opened stub, kill the provider process, and wait for the
        I/O threads to join.

        After this method is called, open needs to be called again if we want to use the provider.
        """
        if self._stub:
            self._stub.Stop(tfplugin5_pb2.Stop.Request())
            self._stub = None

        if self._proc:
            self._proc.kill()
            self._proc.wait(5)
            self._proc = None

        if self._stdout_thread:
            self._stdout_thread.join(5)

        if self._stderr_thread:
            self._stderr_thread.join(5)

    @property
    def schema(self) -> Any:
        if not self._schema:
            self._schema = self._stub.GetSchema(
                tfplugin5_pb2.GetProviderSchema.Request()
            )

        return self._schema

    @property
    def provider_schema(self) -> Any:
        return self.schema.provider

    @property
    def resource_schema(self) -> Any:
        return self.schema.resource_schemas.get(self.resource_state.type_name)

    @property
    def ready(self) -> bool:
        return self._proc is not None and self._stub is not None
