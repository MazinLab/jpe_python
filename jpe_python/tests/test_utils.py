"""
Unit tests for utils.py
"""

import numpy as np
import pytest
from conftest import mock_controller_ctx

import jpe_python.utils as utils
from jpe_python.config import UcsbStageModel
from jpe_python.wrapper import ModuleChannel, Slot


def test_get_pos_samples(mock_controller_ctx):
    mock_controller_ctx.get_current_position.side_effect = [1.0, 6.0, 2.0]
    samples = utils.get_pos_samples(
        mock_controller_ctx, UcsbStageModel.X, ModuleChannel().one, Slot().four, 3
    )
    assert samples.shape == (3,)
    assert samples[0] == 1.0
    assert samples[1] == 6.0
    assert samples[2] == 2.0


def test_get_pos_mean_arithmetic(mock_controller_ctx):
    mock_controller_ctx.get_current_position.side_effect = [1.0, 6.0, 2.0]
    pos_mean = utils.get_pos_mean(
        mock_controller_ctx, UcsbStageModel.X, ModuleChannel().one, Slot().four, 3
    )
    assert pos_mean == 3.0


def test_get_pos_mean_trimmed(mock_controller_ctx):
    # Trimmed mean cuts the top and bottom 10%. Will create a list of 20 values and
    # only consider the middle 18 in the averaging
    ret_vals = [0.0]
    ret_vals.extend([2.0 for _ in range(18)])
    ret_vals.append(1000.0)
    print(len(ret_vals))

    mock_controller_ctx.get_current_position.side_effect = ret_vals
    pos_mean = utils.get_pos_mean(
        mock_controller_ctx,
        UcsbStageModel.X,
        ModuleChannel().one,
        Slot().four,
        len(ret_vals),
        avg_type="trimmed",
    )
    assert pos_mean == 2.0
