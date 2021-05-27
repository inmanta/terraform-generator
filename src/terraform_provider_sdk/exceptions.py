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


class PluginException(Exception):
    def __init__(self, message: str) -> None:
        """
        This error is raised from the plugin client.
        """
        super().__init__(message)


class PluginInitException(PluginException):
    def __init__(self, message: str) -> None:
        """
        This error is raised during the configuration of the plugin client if
        something goes wrong.
        """
        super().__init__(f"Failed to initialize the plugin: {message}")


class InstallerException(Exception):
    def __init__(self, message: str) -> None:
        """
        This error is raised from the plugin installer.
        """
        super().__init__(message)


class InstallerNotReadyException(InstallerException):
    def __init__(self, message: str) -> None:
        """
        This error is raised from the plugin installer whenever some step of the installation
        has been skiped or some resources are not ready/configured correctly.
        """
        super().__init__(message)
