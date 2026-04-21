"""
Utilities to abstract the base API
"""

import time

import numpy as np

from .config import BasedriveStageCfg, ServodriveCfg
from .wrapper import ControllerContext, Direction, Slot


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
        pos = [
            ctx.get_current_position(
                rsm_slot, stage_cfg.rsm_channel, stage_cfg.stage.value
            )
            for _ in range(pos_avg)
        ]
        positions.append(
            ((x + 1) * stage_cfg.num_steps, float(np.average(np.array(pos))))
        )
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
