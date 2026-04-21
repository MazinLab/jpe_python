"""
Types and functions related to API configuration parameters
"""

from dataclasses import dataclass
from enum import Enum

from .wrapper import Direction, ModuleChannel, SetpointPosMode, Slot


class UcsbStageModel(Enum):
    X = "CRD1-RLS"
    Y = "CRD1-RLS"
    Z = "CBS10-RLS"


@dataclass
class BasedriveStageCfg:
    cadm_slot: Slot
    stage: UcsbStageModel
    direction: Direction
    num_steps: int
    temp_K: int
    rsm_channel: ModuleChannel
    step_frequency: int = 600
    relative_step_size: int = 100
    drive_factor: float = 1.0


@dataclass
class ServodriveStageCfg:
    position: float
    setpoint_mode: SetpointPosMode


@dataclass
class ServodriveCfg:
    stage1_cfg: ServodriveStageCfg
    stage2_cfg: ServodriveStageCfg
    stage3_cfg: ServodriveStageCfg
    temp_K: int
    init_step_frequency: int = 600
    drive_factor: float = 1.0
