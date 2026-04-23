"""
Common fixtures and utilities for testing
"""

from unittest.mock import create_autospec

import pytest

from jpe_python.wrapper import ControllerContext


@pytest.fixture
def mock_controller_ctx():
    mock = create_autospec(ControllerContext, instance=True)
    mock.get_current_position.return_value = 10.0
    mock.get_current_position_all.return_value = [2.0, 4.0, 8.0]
    return mock
