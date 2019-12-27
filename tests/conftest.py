# built-in
from pathlib import Path

# external
import pytest


@pytest.fixture
def requirements_path() -> Path:
    """ Return the absolute Path to 'tests/requirements' """
    return Path(__file__).parent / Path('requirements')
