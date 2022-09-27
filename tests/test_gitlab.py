"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import subprocess
import sys
from pathlib import Path


def test_generate_module(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "src/__init__.py",
            "--namespace=gitlabhq",
            "--type=gitlab",
            "--version=3.6.0",
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
        cwd=str(tmp_path / "gitlab"),
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
