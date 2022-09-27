"""
    :copyright: 2022 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
import logging
import re
from pathlib import Path

import inmanta.module

LOGGER = logging.getLogger(__name__)


test_project_compile = re.compile(r"project.compile\((.*)\)")


def upgrade_module_tests(module: inmanta.module.Module) -> None:
    """
    This function can be called on an existing module, to upgrade its basic test
    case to a slightly more advanced one.  This new test will import all of the
    module's sub-modules instead of the top one only.
    """
    basic_test_path = Path(module.path, "tests/test_basics.py")
    if not basic_test_path.exists():
        raise RuntimeError(
            f"Failed to find an existing test file at {str(basic_test_path)}"
        )

    test_case_template = basic_test_path.read_text()
    LOGGER.debug(f"Using existing test as template: \n{test_case_template}")

    sub_modules = module.get_all_submodules()
    LOGGER.debug(f"Found {len(sub_modules)} sub modules")
    import_list = "\nimport ".join(sub_modules)

    current_compiled_model_match = test_project_compile.search(test_case_template)
    assert current_compiled_model_match is not None
    current_compiled_model = current_compiled_model_match.group(1)
    advanced_test_case = test_case_template.replace(
        current_compiled_model, f'"""import {import_list}"""'
    )

    advanced_test_case_path = basic_test_path.parent / "test_advanced.py"
    if advanced_test_case_path.exists():
        raise RuntimeError(f"There is already a file at {advanced_test_case_path}")

    LOGGER.debug(f"Writing extended test case to {advanced_test_case_path}")
    advanced_test_case_path.write_text(advanced_test_case)
