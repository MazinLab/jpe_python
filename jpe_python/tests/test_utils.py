"""
Unit tests for utils.py
"""

import numpy as np
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


def test_get_pos_all_samples(mock_controller_ctx):
    ret_vals = [[1.0, 6.0, 2.0], [3.0, 12.0, 4.0]]
    mock_controller_ctx.get_current_position_all.side_effect = ret_vals
    samples = utils.get_pos_all_samples(
        mock_controller_ctx,
        (UcsbStageModel.X, UcsbStageModel.Y, UcsbStageModel.Z),
        Slot().four,
        len(ret_vals),
    )
    assert samples.shape == (2, 3)
    assert samples[0][0] == 1.0
    assert samples[0][1] == 6.0
    assert samples[0][2] == 2.0
    assert samples[1][0] == 3.0
    assert samples[1][1] == 12.0
    assert samples[1][2] == 4.0


def test_get_pos_all_mean_arithmetic(mock_controller_ctx):
    ret_vals = [[1.0, 6.0, 2.0], [3.0, 12.0, 4.0]]
    mock_controller_ctx.get_current_position_all.side_effect = ret_vals
    samples = utils.get_pos_all_mean(
        mock_controller_ctx,
        (UcsbStageModel.X, UcsbStageModel.Y, UcsbStageModel.Z),
        Slot().four,
        len(ret_vals),
        avg_type="arithmetic",
    )
    assert samples.shape == (3,)
    assert samples[0] == 2.0
    assert samples[1] == 9.0
    assert samples[2] == 3.0


def test_get_pos_all_mean_trimmed(mock_controller_ctx):
    # Trimmed mean cuts the top and bottom 10%. Will create a list of 20 values and
    # only consider the middle 18 in the averaging
    ret_vals = [[0.0, 0.0, 0.0]]
    ret_vals.extend([[1.0, 2.0, 3.0] for _ in range(18)])
    ret_vals.append([1900.0, 1690.0, 2000.0])

    mock_controller_ctx.get_current_position_all.side_effect = ret_vals
    samples = utils.get_pos_all_mean(
        mock_controller_ctx,
        (UcsbStageModel.X, UcsbStageModel.Y, UcsbStageModel.Z),
        Slot().four,
        len(ret_vals),
        avg_type="trimmed",
    )
    assert samples.shape == (3,)
    assert samples[0] == 1.0
    assert samples[1] == 2.0
    assert samples[2] == 3.0
