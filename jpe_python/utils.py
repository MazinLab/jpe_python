"""
Utilities to abstract the base API
"""

import time
from typing import Literal, cast

import numpy as np
from numpy.typing import NDArray
from scipy.stats import trim_mean

from .config import BasedriveStageCfg, ServodriveCfg, UcsbStageModel
from .wrapper import (
    ControllerContext,
    ControllerOpMode,
    Direction,
    ModuleChannel,
    SetpointPosMode,
    Slot,
)

PositionMeanType = Literal["arithmetic", "trimmed"]


def get_pos_all_mean(
    ctx: ControllerContext,
    stages: tuple[UcsbStageModel, UcsbStageModel, UcsbStageModel],
    rsm_slot: Slot,
    n_samples: int,
    avg_type: PositionMeanType = "arithmetic",
) -> NDArray:

    # Get samples
    ret = get_pos_all_samples(ctx, stages, rsm_slot, n_samples)

    match avg_type:
        case "arithmetic":
            ret = trim_mean(ret, 0, axis=0)
        case "trimmed":
            ret = trim_mean(ret, 0.1, axis=0)

    # Cast needed here because trim_mean has poor return type hinting
    return cast(NDArray, ret)


def get_pos_all_samples(
    ctx: ControllerContext,
    stages: tuple[UcsbStageModel, UcsbStageModel, UcsbStageModel],
    rsm_slot: Slot,
    n_samples: int,
) -> NDArray:
    # Preallocate array
    ret = np.zeros((n_samples, 3), dtype=np.float64)
    success_cnt = 0

    # Fallibly poll the compressor for position data. Will not catch fatal errors.
    for it in range(n_samples):
        try:
            ret[it, :] = ctx.get_current_position_all(
                rsm_slot, stages[0].value, stages[1].value, stages[2].value
            )
        except ValueError as e:
            print(f"Value error on poll #{it + 1}: {e}. Continuing...")
            continue
        success_cnt += 1
    # Truncate any empty rows
    return ret[:success_cnt]


def get_pos_samples(
    ctx: ControllerContext,
    stage: UcsbStageModel,
    rsm_channel: ModuleChannel,
    rsm_slot: Slot,
    n_samples: int,
) -> NDArray:
    # Preallocate array
    ret = np.zeros(n_samples, dtype=np.float64)
    success_cnt = 0

    # Fallibly poll the compressor for position data. Will not catch fatal errors.
    for it in range(n_samples):
        try:
            ret[it] = ctx.get_current_position(rsm_slot, rsm_channel, stage.value)
        except ValueError as e:
            print(f"Value error on poll #{it + 1}: {e}. Continuing...")
            continue
        success_cnt += 1
    # Truncate any empty rows
    return ret[:success_cnt]


def get_pos_mean(
    ctx: ControllerContext,
    stage: UcsbStageModel,
    rsm_slot: Slot,
    rsm_channel: ModuleChannel,
    n_samples: int,
    avg_type: PositionMeanType = "arithmetic",
) -> float:

    # Get samples
    ret = get_pos_samples(ctx, stage, rsm_channel, rsm_slot, n_samples)

    match avg_type:
        case "arithmetic":
            ret = trim_mean(ret, 0)
        case "trimmed":
            ret = trim_mean(ret, 0.1)
    return ret


def move_stage_n_rsm(
    ctx: ControllerContext,
    rsm_slot: Slot,
    stage_cfg: BasedriveStageCfg,
    n_iter: int = 10,
    pos_avg: int = 1,
    step_delay: int = 1,
    reset: bool = False,
) -> list[tuple[float, float]]:
    """
    Moves the stage `n_iter` times and returns the position
    as read by the RSM module on the given channel along with the
    cumulative number of steps taken.

    The total number of steps taken will be based on the number of steps per
    actuation specified in `stage_cfg`.

    Args:
        n_iter: Number of times the stage will be told to actuate, based on passed BasedriveStageCfg
        pos_avg: Number of times to read the position for each actuation. These values will then be averaged.
        step_delay: The number of seconds to wait between actuations.
        reset: It True, the stage will to return to its initial position.

    Returns:
        A list of tuples, where each tuple is (accumulated_steps, position_in_meters).
        The returned list will have length `n_iter` + 1, the first element is the initial position.
        For example: If the stage moves 100 steps per actuation, the third list element be (200, stage_position_in_meters).
    """

    positions: list[tuple[float, float]] = []
    # Add starting position to list before moving
    positions.append(
        (
            0,
            ctx.get_current_position(
                rsm_slot, stage_cfg.rsm_channel, stage_cfg.stage.value
            ),
        )
    )
    for x in range(n_iter):
        ctx.move_stage_open(
            stage_cfg.cadm_slot,
            stage_cfg.direction,
            stage_cfg.step_frequency,
            stage_cfg.relative_step_size,
            stage_cfg.num_steps,
            stage_cfg.temp_K,
            stage_cfg.stage.value,
            stage_cfg.drive_factor,
        )
        # Take position measurements and average
        avg_pos = get_pos_mean(
            ctx, stage_cfg.stage, rsm_slot, stage_cfg.rsm_channel, pos_avg
        )
        positions.append(((x + 1) * stage_cfg.num_steps, avg_pos))
        time.sleep(step_delay)

    # Reset the stage back to start
    if stage_cfg.direction == Direction().pos:
        rev_stage_dir = Direction().neg
    else:
        rev_stage_dir = Direction().pos

    if reset:
        ctx.move_stage_open(
            stage_cfg.cadm_slot,
            rev_stage_dir,
            stage_cfg.step_frequency,
            stage_cfg.relative_step_size,
            stage_cfg.num_steps * (len(positions) - 1),
            stage_cfg.temp_K,
            stage_cfg.stage.value,
            stage_cfg.drive_factor,
        )
    return positions


def reset_stages_center_samples(
    ctx: ControllerContext, poll_rate: int = 500, raw_pos: bool = False
) -> NDArray | None:
    """
    Moves all stages the their respective centers in servodrive mode.


    Args:
        `poll_rate`: How often to poll the controller for status updates on the control loop.
        `raw_pos`: Toggles whether to return the raw final position samples or their averages (see Returns section)
        step_delay: The number of seconds to wait between actuations.
        reset: It True, the stage will to return to its initial position.

    Returns:
        If `raw_pos` is `True`:
            A tuple containing three lists where each list constains the raw position samples for the given stage.
            E.g. (stage1_pos_samples, stage2_pos_samples, stage3_pos_samples)
        Otherwise:
            A tuple with the arithmetic mean of the position for each stage.
            E.g. (stage1_pos_mean, stage2_pos_mean, stage3_pos_mean)
    """
    # 1. Enable servodrive mode
    # 2. Command ALL stages to move to the center of their travel using
    # absolute positioning
    # 3. Poll the control loop until it either finishes or errors
    #   - First poll will be to validate that the control loop is enabled and all passed setpoints were valid
    #   - Poll rate passed by caller in milliseconds
    #   - Print the progress to stdout
    #   - Format:
    #   - First Poll: CONTROL LOOP ENABLED/DISABLED | ALL SETPOINTS VALID or STAGE[1,2,3] SETPOINT INVALID | RUNNING...
    #       - If all setpoints are invalid, return early with the None
    #   - Happy Path: Iteration: 0 | Stage 1 Error: 10um | Stage 2 Error: -0.004um | Stage 3 Error: 3um | RUNNING... or COMPLETE
    #   - Error Path: Iteration: 12 | Exception: a nasty, dirty error occurred
    return None
