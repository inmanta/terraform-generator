"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import pathlib
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    argnames=(
        "namespace",
        "provider_type",
        "version",
    ),
    argvalues=[
        (
            "hashicorp",
            "local",
            "2.1.0",
        ),
        (
            "fortinetdev",
            "fortios",
            "1.11.0",
        ),
        (
            "CheckpointSW",
            "checkpoint",
            "1.4.0",
        ),
        (
            "gitlabhq",
            "gitlab",
            "3.6.0",
        ),
        (
            "integrations",
            "github",
            "4.10.1",
        ),
        (
            "kreuzwerker",
            "docker",
            "2.22.0",
        ),
    ],
)
def test_generate_module(
    tmp_path: pathlib.Path, namespace: str, provider_type: str, version: str
) -> None:
    """
    This basic test will generate a new module based on the provider specified in arguments
    and run the generated tests of the module against it.
    """
    result = subprocess.run(
        [
            sys.executable,
            "src/__init__.py",
            f"--namespace={namespace}",
            f"--type={provider_type}",
            f"--version={version}",
            str(tmp_path),
        ],
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
        ],
        cwd=str(tmp_path / provider_type),
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
