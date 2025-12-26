"""Data models for printer components."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TemperatureSensor:
    """Temperature sensor data."""
    name: str
    temperature: float
    measured_min_temp: Optional[float] = None
    measured_max_temp: Optional[float] = None
    target: Optional[float] = None
    power: Optional[float] = None


@dataclass
class Fan:
    """Fan data."""
    name: str
    speed: float
    rpm: Optional[float] = None


@dataclass
class LED:
    """LED/Neopixel data."""
    name: str
    color_data: Optional[list] = None


@dataclass
class Macro:
    """Klipper macro."""
    name: str
    description: Optional[str] = None
    parameters: Optional[list[str]] = None
    gcode: Optional[str] = None
    variables: Optional[dict] = None


@dataclass
class Heater:
    """Heater data."""
    name: str
    temperature: float
    target: float
    power: float


@dataclass
class Pin:
    """Output pin data."""
    name: str
    value: float


@dataclass
class GCodeCommand:
    """G-code command help information."""
    name: str
    description: str


@dataclass
class PrinterState:
    """Overall printer state."""
    state: str
    state_message: str


@dataclass
class Toolhead:
    """Toolhead status including homing state."""
    homed_axes: str
    position: list[float]
    print_time: float
    estimated_print_time: float


@dataclass
class Endstops:
    """Endstop status."""
    endstops: dict[str, str]


@dataclass
class GCodeFile:
    """G-code file information."""
    filename: str
    size: int
    modified: float
    # Optional metadata fields
    estimated_time: Optional[float] = None
    filament_total: Optional[float] = None
    first_layer_height: Optional[float] = None
    layer_height: Optional[float] = None
    object_height: Optional[float] = None
    slicer: Optional[str] = None
    thumbnails: Optional[list] = None


@dataclass
class Directory:
    """Directory information."""
    dirname: str
    size: int
    modified: float
    permissions: Optional[str] = None


@dataclass
class PrintStatus:
    """Print job status information."""
    state: str  # standby, printing, paused, complete, cancelled, error
    filename: str
    total_duration: float  # Total time since print started
    print_duration: float  # Actual printing time (excludes paused time)
    filament_used: float  # mm of filament used
    progress: float  # 0.0 to 1.0
    message: str  # Current status message


@dataclass
class ConsoleMessage:
    """Console message from Klipper."""
    message: str
    time: float
    type: str = "response"  # response, command, error, warning


__all__ = [
    "TemperatureSensor",
    "Fan",
    "LED",
    "Macro",
    "Heater",
    "Pin",
    "GCodeCommand",
    "PrinterState",
    "Toolhead",
    "Endstops",
    "GCodeFile",
    "Directory",
    "PrintStatus",
    "ConsoleMessage",
]
