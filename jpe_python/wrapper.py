"""
Convenience wrappers for the JPE rust-python FFI. Allows for type-hints, docstrings,
etc while using Python development tools.
"""
import jpe_python_ffi # type: ignore

class Slot:
    """
    Enum that signifies a slot within the controller cabinet.
    """
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.Slot
        self.one = self.inner.one()
        self.two = self.inner.two()
        self.three = self.inner.three()
        self.four = self.inner.four()
        self.five = self.inner.five()
        self.six = self.inner.six()
    @classmethod
    def from_str(cls, s: str):
        return jpe_python_ffi.Slot.from_string(s)
    
class SerialInterface:
    """
    Enum that presents the supported serial interface modes.
    """
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.SerialInterface
        self.usb = self.inner.usb()
        self.rs422 = self.inner.rs422()

class IpAddrMode:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.IpAddrMode
        self.dhcp = self.inner.dhcp()
        self.static = self.inner.stat()
class Module:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.Module
        self.cadm = self.inner.cadm()
        self.rsm = self.inner.rsm()
        self.oem = self.inner.oem()
        self.psm = self.inner.psm()
        self.edm = self.inner.edm()
    @classmethod
    def from_str(cls, s: str):
        return jpe_python_ffi.Module.from_string(s)
class ControllerOpMode:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.ControllerOpMode
        self.base = self.inner.base()
        self.servo = self.inner.servo()
        self.flex = self.inner.flex()
class ConnMode:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.ConnMode
        self.serial = self.inner.serial()
        self.network = self.inner.network()
class ModuleChannel:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.ModuleChannel
        self.one = self.inner.one()
        self.two = self.inner.two()
        self.three = self.inner.three()
class Direction:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.Direction
        self.pos = self.inner.pos()
        self.neg = self.inner.neg()
class SetpointPosMode:
    def __init__(self) -> None:
        self.inner = jpe_python_ffi.SetpointPosMode
        self.rel = self.inner.rel()
        self.abs = self.inner.abs()

class ControllerContext:
    """
    Context that contains commands to administer the controller
    """
    def __init__(self, inner) -> None:
        self.inner  = inner

    @classmethod
    def with_network(cls, ip: str):
        """
        Constructor returning context using network transport
        """
        return ControllerContext(jpe_python_ffi.BaseContextBuilder().with_network(ip).build())

    @classmethod
    def with_serial(cls, com: str, baud: int = 115200):
        """
        Constructor returning context using serial transport
        """
        ctx = jpe_python_ffi.BaseContextBuilder().with_serial(com)
        if baud != 115200:
            ctx = ctx.baud(baud)
        return ControllerContext(ctx.build())

    def get_fw_version(self) -> str:
        """
        Returns the firmware version of the controller and updates internal value.
        """
        return self.inner.get_fw_version()

    def get_mod_fw_version(self, slot: Slot) -> str:
        """
        Returns firmware version information of module in given slot. Returns None if slot is empty.
        """
        return self.inner.get_mod_fw_version(slot)

    def get_module_list(self) -> list[str]:
        """
        Returns a list of all installed modules and updates internal module container.
        """
        return self.inner.get_module_list()

    def get_supported_stages(self) -> list[str]:
        """
        Returns a list of supported actuator and stage types.
        """
        return self.inner.get_supported_stages()

    def get_ip_config(self) -> list[str]:
        """
        Returns IP configuration for the LAN interface.

        Response: [MODE],[IP address],[Subnet Mask],[Gateway],[MAC Address]
        """
        return self.inner.get_ip_config()

    def set_ip_config(
        self,
        addr_mode: IpAddrMode,
        ip_addr: str,
        mask: str,
        gateway: str) -> str:
        """
        Sets the IP configuration for the LAN interface.
        """
        return self.inner.set_ip_config_py(addr_mode, ip_addr, mask, gateway)

    def get_baud_rate(self, ifc: SerialInterface) -> int:
        """
        Get baudrate setting for the USB or RS-422 interface.
        """
        return self.inner.get_baud_rate(ifc)

    def set_baud_rate(self, ifc: SerialInterface, baud: int) -> str:
        """
        Set the baudrate for the USB or RS-422 interface on the controller.
        """
        return self.inner.set_baud_rate(ifc, baud)

    def start_mod_fw_update(self, fname: str, slot: Slot):
        """
        Instructs a module to update its firmware based on the given filename.
        Firmware must be uploaded to the controller via the web interface and must match the passed filename.

        Note: The controller will respond only once the firmware is fully updated (may take a long time).
        """
        return self.inner.start_mod_fw_update(fname, slot)

    def get_fail_safe_state(self, slot: Slot) -> str:
        """
        Get the fail-safe state of the CADM2 module.
        """
        return self.inner.get_fail_safe_state(slot)

    def move_stage_open(
        self,
        slot: Slot,
        direction: Direction,
        step_freq: int,
        r_step_size: int,
        n_steps: int,
        temp: int,
        stage: str,
        drive_factor: float,
    ) -> str:
        """
        Starts moving an actuator or positioner with specified parameters in open loop mode. Supported on
        CADM2 modules.
        """
        return self.inner.move_stage_open(slot, direction, step_freq, r_step_size, n_steps, temp, stage, drive_factor)
    def stop_stage(self, slot: Slot) -> str:
        """
        Stops movement of an actuator (MOV command), disables external input mode (EXT command,
        breaks out of Flexdrive mode) or disables scan mode (SDC command).
        """
        return self.inner.stop_stage(slot)
    def enable_scan_mode(self, slot: Slot, level: int) -> str:
        """
        CADM module will output a DC voltage level (to be used with a scanner piezo for example) instead of
        the default drive signal. `level` can be set to a value in between 0 and 1023 where zero represents
        ~0[V] output (-30[V] with respect to REF) and the maximum value represents ~150[V]
        output (+120[V] with respect to REF)
        """
        return self.inner.enable_scan_mode(slot, level)
    def enable_ext_input_mode(
        self,
        slot: Slot,
        direction: Direction,
        step_freq: int,
        r_step_size: int,
        temp: int,
        stage: str,
        drive_factor: float,
    ) -> str:
        """
        Sets the CADM in external control mode (Flexdrive mode). Similar to MOV, but
        `step_freq` now defines the step frequency at maximum (absolute) input signal. By
        default, set this to 600 [Hz]. `direction` now modulates the stage movement direction
        with respect to the polarity of the external input signal (E.g Negative -> positive external signal voltage drives
        the stage in the negative direction).
        """
        return self.inner.enable_ext_input_mode(slot, direction, step_freq, r_step_size, temp, stage, drive_factor)
    def get_current_position(
        self,
        slot: Slot,
        ch: ModuleChannel,
        stage: str,
    ) -> float:
        """
        Get the position of a Resistive Linear Sensor (RLS) connected to a specific channel of the RSM
        module. Return value is in meters.
        """
        return self.inner.get_current_position(slot, ch, stage)
    def get_current_position_all(
        self,
        slot: Slot,
        stage_ch1: str,
        stage_ch2: str,
        stage_ch3: str,
    ) -> list[float]:
        """
        Get the position of all three channels of the RSM simultaneously. Return values are in meters.
        """
        return self.inner.get_current_position_all(slot, stage_ch1, stage_ch2, stage_ch3)
    def set_neg_end_stop(self, slot: Slot, ch: ModuleChannel) -> str:
        """
        Set the current position of a Resistive Linear Sensor (RLS) connected to channel `ch` of the RSM to be
        the negative end-stop. To be used as part of the RLS Calibration process.
        """
        return self.inner.set_neg_end_stop(slot, ch)
    def set_pos_end_stop(self, slot: Slot, ch: ModuleChannel) -> str:
        """
        Set the current position of a Resistive Linear Sensor (RLS) connected to channel `ch` of the RSM to be
        the positive end-stop. To be used as part of the RLS Calibration process.
        """
        return self.inner.set_pos_end_stop(slot, ch)
    def read_neg_end_stop(
        self,
        slot: Slot,
        ch: ModuleChannel,
        stage: str,
    ) -> float:
        """
        Read the current value of the negative end-stop parameter set for a channel `ch` of an RSM.
        Response value is in meters.
        """
        return self.inner.read_neg_end_stop(slot, ch, stage)
    def read_pos_end_stop(
        self,
        slot: Slot,
        ch: ModuleChannel,
        stage: str,
    ) -> float:
        """
        Read the current value of the positive end-stop parameter set for a channel `ch` of an RSM.
        Response value is in meters.
        """
        return self.inner.read_pos_end_stop(slot, ch, stage)
    def reset_end_stops(self, slot: Slot, ch: ModuleChannel) -> str:
        """
        Reset the current values of the negative and positive end-stop parameters set for channel `ch`
        of an RSM to values stored in controller NV-RAM.
        """
        return self.inner.reset_end_stops(slot, ch)
    def set_excitation_ds(self, slot: Slot, duty: int) -> str:
        """
        Set the duty cycle of the sensor excitation signal of the RSM for all channels. `duty` is a percentage and can
        be set to 0 or from 10 to 100.
        """
        return self.inner.set_excitation_ds(slot, duty)
    def read_excitation_ds(self, slot: Slot) -> int:
        """
        Read the duty cycle of the sensor excitation signal for all channels of an RSM.
        Response value is a percentage.
        """
        return self.inner.read_excitation_ds(slot)
    def save_rsm_nvram(self, slot: Slot) -> str:
        """
        Store the current values of the following parameters of an RSM to the non-volatile memory of the
        controller: excitation duty cycle (EXS), negative end stop (MIS) and positive end-stop (MAS).
        """
        return self.inner.save_rsm_nvram(slot)
    def enable_servodrive(
        self,
        stage_1: str,
        init_step_freq_1: int,
        stage_2: str,
        init_step_freq_2: int,
        stage_3: str,
        init_step_freq_3: int,
        temp: int,
        drive_factor: float,
    ) -> str:
        """
        Enable the internal position feedback control and start operating in Servodrive mode with up to three
        different stages. Initial step frequency is used to adjust how fast the stages initially take steps (the control
        loop will reduce this as a setpoint is approached).
        """
        return self.inner.enable_servodrive(stage_1, init_step_freq_1, stage_2, init_step_freq_2, stage_3, init_step_freq_3, temp, drive_factor)
    def disable_servodrive(self) -> str:
        """
        Disable the internal position feedback control.
        """
        return self.inner.disable_servodrive()
    def servodrive_em_stop(self) -> str:
        """
        The servodrive control loop will be immediately aborted and the actuators will stop at their current location.
        """
        return self.inner.servodrive_em_stop()
    def go_to_setpoint(
        self,
        set_point1: float,
        pos_mode_1: SetpointPosMode,
        set_point2: float,
        pos_mode_2: SetpointPosMode,
        set_point3: float,
        pos_mode_3: SetpointPosMode,
    ) -> str:
        """
        In servodrive mode, use this command to move actuators to a set point position. For linear type actuators,
        setpoint value is in meters, for rotational, radians. See application notes for description of position mode.
        If there is no actuator/stage connected to one of the outputs, enter 0 as position set point.
        """
        return self.inner.go_to_setpoint(set_point1, pos_mode_1, set_point2, pos_mode_2, set_point3, pos_mode_3)
    def get_servodrive_status(self) -> list[int]:
        """
        Returns a (comma-separated) list with status and position error information for the servodrive
        control loop.

        Response: [ENABLED] [FINISHED] [INVALID SP1] [INVALID SP2] [INVALID SP3] [POS ERROR1] [POS ERROR2] [POS ERROR3]
        NOTE: position error is dimensionless!
        """
        return self.inner.get_servodrive_status()