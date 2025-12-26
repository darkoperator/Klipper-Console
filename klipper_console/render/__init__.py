"""Output rendering and formatting."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from typing import Any
from ..models import TemperatureSensor, Fan, LED, Heater, Pin, Macro, GCodeCommand, Toolhead, Endstops, PrinterState, GCodeFile, Directory, PrintStatus, ConsoleMessage


console = Console()


def render_result(result: Any) -> None:
    """
    Render command result to console.

    Args:
        result: Command result to render
    """
    if result is None:
        return

    if isinstance(result, str):
        console.print(result)
    elif isinstance(result, list):
        if not result:
            console.print("[dim]No items[/dim]")
        elif isinstance(result[0], str):
            # List of strings (e.g., macro names, file names)
            console.print(f"[dim]Found {len(result)} items:[/dim]")
            for item in result:
                console.print(f"  {item}")
        elif isinstance(result[0], TemperatureSensor):
            _render_sensors(result)
        elif isinstance(result[0], Fan):
            _render_fans(result)
        elif isinstance(result[0], LED):
            _render_leds(result)
        elif isinstance(result[0], Heater):
            _render_heaters(result)
        elif isinstance(result[0], Pin):
            _render_pins(result)
        elif isinstance(result[0], GCodeFile):
            _render_gcode_files(result)
        elif isinstance(result[0], Directory):
            _render_directories(result)
        elif isinstance(result[0], ConsoleMessage):
            _render_console_messages(result)
        else:
            # Generic list
            for item in result:
                console.print(item)
    elif isinstance(result, TemperatureSensor):
        _render_sensor(result)
    elif isinstance(result, Fan):
        _render_fan(result)
    elif isinstance(result, LED):
        _render_led(result)
    elif isinstance(result, Heater):
        _render_heater(result)
    elif isinstance(result, Pin):
        _render_pin(result)
    elif isinstance(result, Macro):
        _render_macro(result)
    elif isinstance(result, GCodeCommand):
        _render_gcode_command(result)
    elif isinstance(result, Toolhead):
        _render_toolhead(result)
    elif isinstance(result, Endstops):
        _render_endstops(result)
    elif isinstance(result, PrinterState):
        _render_printer_state(result)
    elif isinstance(result, GCodeFile):
        _render_gcode_file(result)
    elif isinstance(result, Directory):
        _render_directory(result)
    elif isinstance(result, PrintStatus):
        _render_print_status(result)
    else:
        # Fallback
        console.print(result)


def _render_sensors(sensors: list[TemperatureSensor]) -> None:
    """Render list of sensors as table."""
    table = Table(title="Temperature Sensors")
    table.add_column("Name", style="cyan")
    table.add_column("Temperature", justify="right")
    table.add_column("Min", justify="right", style="dim")
    table.add_column("Max", justify="right", style="dim")
    table.add_column("Target", justify="right")
    table.add_column("Power", justify="right")

    for sensor in sensors:
        table.add_row(
            sensor.name,
            f"{sensor.temperature:.1f}°C",
            f"{sensor.measured_min_temp:.1f}°C" if sensor.measured_min_temp else "-",
            f"{sensor.measured_max_temp:.1f}°C" if sensor.measured_max_temp else "-",
            f"{sensor.target:.1f}°C" if sensor.target is not None else "-",
            f"{sensor.power*100:.0f}%" if sensor.power is not None else "-"
        )

    console.print(table)


def _render_sensor(sensor: TemperatureSensor) -> None:
    """Render single sensor."""
    console.print(f"[cyan]{sensor.name}[/cyan]")
    console.print(f"  Temperature: {sensor.temperature:.1f}°C")
    if sensor.measured_min_temp is not None:
        console.print(f"  Min: {sensor.measured_min_temp:.1f}°C")
    if sensor.measured_max_temp is not None:
        console.print(f"  Max: {sensor.measured_max_temp:.1f}°C")
    if sensor.target is not None:
        console.print(f"  Target: {sensor.target:.1f}°C")
    if sensor.power is not None:
        console.print(f"  Power: {sensor.power*100:.0f}%")


def _render_fans(fans: list[Fan]) -> None:
    """Render list of fans as table."""
    table = Table(title="Fans")
    table.add_column("Name", style="cyan")
    table.add_column("Speed", justify="right")
    table.add_column("RPM", justify="right")

    for fan in fans:
        table.add_row(
            fan.name,
            f"{fan.speed*100:.0f}%",
            f"{fan.rpm:.0f}" if fan.rpm else "-"
        )

    console.print(table)


def _render_fan(fan: Fan) -> None:
    """Render single fan."""
    console.print(f"[cyan]{fan.name}[/cyan]")
    console.print(f"  Speed: {fan.speed*100:.0f}%")
    if fan.rpm:
        console.print(f"  RPM: {fan.rpm:.0f}")


def _render_leds(leds: list[LED]) -> None:
    """Render list of LEDs."""
    table = Table(title="LEDs")
    table.add_column("Name", style="cyan")
    table.add_column("Status")

    for led in leds:
        status = "configured" if led.color_data else "off"
        table.add_row(led.name, status)

    console.print(table)


def _render_led(led: LED) -> None:
    """Render single LED."""
    console.print(f"[cyan]{led.name}[/cyan]")
    if led.color_data:
        console.print(f"  Color data: {led.color_data}")
    else:
        console.print("  Status: off")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]Error:[/red] {message}")


def _render_heaters(heaters: list[Heater]) -> None:
    """Render list of heaters as table."""
    table = Table(title="Heaters")
    table.add_column("Name", style="cyan")
    table.add_column("Temperature", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Power", justify="right")

    for heater in heaters:
        # Color code based on state
        if heater.target > 0:
            temp_style = "yellow" if heater.temperature < heater.target - 5 else "green"
            temp_text = f"[{temp_style}]{heater.temperature:.1f}°C[/{temp_style}]"
        else:
            temp_text = f"{heater.temperature:.1f}°C"

        table.add_row(
            heater.name,
            temp_text,
            f"{heater.target:.1f}°C" if heater.target > 0 else "-",
            f"{heater.power*100:.0f}%"
        )

    console.print(table)


def _render_heater(heater: Heater) -> None:
    """Render single heater."""
    console.print(f"[cyan]{heater.name}[/cyan]")

    # Color code temperature
    if heater.target > 0:
        temp_style = "yellow" if heater.temperature < heater.target - 5 else "green"
        console.print(f"  Temperature: [{temp_style}]{heater.temperature:.1f}°C[/{temp_style}]")
    else:
        console.print(f"  Temperature: {heater.temperature:.1f}°C")

    console.print(f"  Target: {heater.target:.1f}°C")
    console.print(f"  Power: {heater.power*100:.0f}%")


def _render_pins(pins: list[Pin]) -> None:
    """Render list of pins as table."""
    table = Table(title="Output Pins")
    table.add_column("Name", style="cyan")
    table.add_column("Value", justify="right")

    for pin in pins:
        table.add_row(
            pin.name,
            f"{pin.value:.2f}"
        )

    console.print(table)


def _render_pin(pin: Pin) -> None:
    """Render single pin."""
    console.print(f"[cyan]{pin.name}[/cyan]")
    console.print(f"  Value: {pin.value:.2f}")


def _render_macro(macro: Macro) -> None:
    """Render detailed macro information."""
    # Header
    console.print(f"\n[bold cyan]Macro: {macro.name}[/bold cyan]")

    # Description
    if macro.description:
        console.print(f"[dim]Description:[/dim] {macro.description}")

    # Parameters
    if macro.parameters:
        console.print(f"\n[dim]Parameters:[/dim]")
        for param in macro.parameters:
            console.print(f"  • {param}")
    else:
        console.print(f"\n[dim]Parameters:[/dim] None")

    # Usage example
    if macro.parameters:
        example_params = " ".join([f"{p}=<value>" for p in macro.parameters[:3]])
        console.print(f"\n[dim]Usage:[/dim]")
        console.print(f"  run {macro.name} {example_params}")
    else:
        console.print(f"\n[dim]Usage:[/dim]")
        console.print(f"  run {macro.name}")

    # G-code preview (optional, can be commented out if too verbose)
    if macro.gcode and len(macro.gcode) < 200:
        console.print(f"\n[dim]G-code:[/dim]")
        # Show first few lines
        lines = macro.gcode.strip().split('\n')[:5]
        for line in lines:
            if line.strip():
                console.print(f"  {line}")
        if len(macro.gcode.split('\n')) > 5:
            console.print(f"  [dim]... ({len(macro.gcode.split('\n'))} lines total)[/dim]")


def _render_gcode_command(gcode_cmd: GCodeCommand) -> None:
    """Render G-code command help information."""
    console.print(f"\n[bold cyan]G-code: {gcode_cmd.name}[/bold cyan]")
    console.print(f"[dim]Description:[/dim] {gcode_cmd.description}")

    # Usage
    console.print(f"\n[dim]Usage:[/dim]")
    console.print(f"  run_gcode {gcode_cmd.name}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def _render_toolhead(toolhead: Toolhead) -> None:
    """Render toolhead status."""
    console.print(f"\n[bold cyan]Toolhead Status[/bold cyan]")

    # Homing status
    if toolhead.homed_axes:
        axes_list = list(toolhead.homed_axes.lower())
        homed_status = f"[green]Homed: {', '.join(axes_list).upper()}[/green]"
    else:
        homed_status = "[red]Not homed[/red]"

    console.print(f"  {homed_status}")

    # Position
    console.print(f"\n[dim]Position:[/dim]")
    console.print(f"  X: {toolhead.position[0]:.2f} mm")
    console.print(f"  Y: {toolhead.position[1]:.2f} mm")
    console.print(f"  Z: {toolhead.position[2]:.2f} mm")
    console.print(f"  E: {toolhead.position[3]:.2f} mm")


def _render_endstops(endstops: Endstops) -> None:
    """Render endstop status."""
    console.print(f"\n[bold cyan]Endstop Status[/bold cyan]")

    if not endstops.endstops:
        console.print("  [dim]No endstops found[/dim]")
        return

    # Create table
    table = Table(show_header=True)
    table.add_column("Endstop", style="cyan")
    table.add_column("State", justify="center")

    for name, state in sorted(endstops.endstops.items()):
        # Color code the state
        if state.lower() == "triggered" or state.lower() == "open":
            state_text = f"[red]{state}[/red]"
        else:
            state_text = f"[green]{state}[/green]"

        table.add_row(name, state_text)

    console.print(table)


def _render_printer_state(state: PrinterState) -> None:
    """Render printer state."""
    console.print(f"\n[bold cyan]Printer Status[/bold cyan]")

    # Color code based on state
    if state.state == "ready":
        state_text = f"[green]{state.state.upper()}[/green]"
    elif state.state == "error" or state.state == "shutdown":
        state_text = f"[red]{state.state.upper()}[/red]"
    elif state.state == "printing":
        state_text = f"[yellow]{state.state.upper()}[/yellow]"
    else:
        state_text = f"[cyan]{state.state.upper()}[/cyan]"

    console.print(f"  State: {state_text}")

    if state.state_message:
        console.print(f"  Message: {state.state_message}")


def _render_gcode_file(file: GCodeFile) -> None:
    """Render detailed G-code file information."""
    console.print(f"\n[bold cyan]File: {file.filename}[/bold cyan]")

    # Basic info
    size_mb = file.size / (1024 * 1024)
    console.print(f"  Size: {size_mb:.2f} MB")

    # Format timestamp
    from datetime import datetime
    modified_dt = datetime.fromtimestamp(file.modified)
    console.print(f"  Modified: {modified_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    # Metadata if available
    if file.estimated_time:
        hours = int(file.estimated_time // 3600)
        minutes = int((file.estimated_time % 3600) // 60)
        console.print(f"\n[dim]Print Info:[/dim]")
        console.print(f"  Estimated time: {hours}h {minutes}m")

    if file.filament_total:
        filament_m = file.filament_total / 1000
        console.print(f"  Filament: {filament_m:.2f} m")

    if file.first_layer_height:
        console.print(f"  First layer height: {file.first_layer_height} mm")

    if file.layer_height:
        console.print(f"  Layer height: {file.layer_height} mm")

    if file.object_height:
        console.print(f"  Object height: {file.object_height} mm")

    if file.slicer:
        console.print(f"\n[dim]Slicer:[/dim] {file.slicer}")


def _render_gcode_files(files: list[GCodeFile]) -> None:
    """Render list of G-code files as table."""
    table = Table(title="G-code Files")
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Est. Time", justify="right")
    table.add_column("Modified", justify="right")

    for file in files:
        size_mb = file.size / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB"

        if file.estimated_time:
            hours = int(file.estimated_time // 3600)
            minutes = int((file.estimated_time % 3600) // 60)
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = "-"

        from datetime import datetime
        modified_dt = datetime.fromtimestamp(file.modified)
        modified_str = modified_dt.strftime('%Y-%m-%d %H:%M')

        table.add_row(file.filename, size_str, time_str, modified_str)

    console.print(table)


def _render_directories(directories: list[Directory]) -> None:
    """Render list of directories as table."""
    from datetime import datetime

    table = Table(title="Directories")
    table.add_column("Directory", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", justify="right")
    table.add_column("Permissions", justify="center")

    for directory in directories:
        # Format size
        if directory.size > 1024 * 1024:
            size_str = f"{directory.size / (1024 * 1024):.2f} MB"
        elif directory.size > 1024:
            size_str = f"{directory.size / 1024:.2f} KB"
        else:
            size_str = f"{directory.size} B"

        # Format timestamp
        modified_dt = datetime.fromtimestamp(directory.modified)
        modified_str = modified_dt.strftime('%Y-%m-%d %H:%M')

        table.add_row(
            directory.dirname,
            size_str,
            modified_str,
            directory.permissions or "-"
        )

    console.print(table)


def _render_directory(directory: Directory) -> None:
    """Render single directory details."""
    from datetime import datetime

    console.print(f"\n[bold cyan]Directory: {directory.dirname}[/bold cyan]")

    size_mb = directory.size / (1024 * 1024)
    console.print(f"  Size: {size_mb:.2f} MB")

    modified_dt = datetime.fromtimestamp(directory.modified)
    console.print(f"  Modified: {modified_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    if directory.permissions:
        console.print(f"  Permissions: {directory.permissions}")


def _render_print_status(status: PrintStatus) -> None:
    """Render print job status."""
    console.print(f"\n[bold cyan]Print Status[/bold cyan]")

    # Color code based on state
    if status.state == "printing":
        state_text = f"[yellow]{status.state.upper()}[/yellow]"
    elif status.state == "complete":
        state_text = f"[green]{status.state.upper()}[/green]"
    elif status.state == "error" or status.state == "cancelled":
        state_text = f"[red]{status.state.upper()}[/red]"
    elif status.state == "paused":
        state_text = f"[yellow]{status.state.upper()}[/yellow]"
    else:
        state_text = f"[dim]{status.state.upper()}[/dim]"

    console.print(f"  State: {state_text}")

    # Show filename if printing
    if status.filename:
        console.print(f"  File: {status.filename}")

    # Show progress if printing
    if status.state in ["printing", "paused"] and status.progress > 0:
        progress_pct = status.progress * 100
        console.print(f"  Progress: {progress_pct:.1f}%")

        # Progress bar
        bar_width = 30
        filled = int(bar_width * status.progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        console.print(f"  [{bar}]")

    # Show timing information
    if status.print_duration > 0 or status.total_duration > 0:
        console.print(f"\n[dim]Timing:[/dim]")

        if status.print_duration > 0:
            hours = int(status.print_duration // 3600)
            minutes = int((status.print_duration % 3600) // 60)
            seconds = int(status.print_duration % 60)
            console.print(f"  Print time: {hours:02d}:{minutes:02d}:{seconds:02d}")

        if status.total_duration > 0:
            hours = int(status.total_duration // 3600)
            minutes = int((status.total_duration % 3600) // 60)
            seconds = int(status.total_duration % 60)
            console.print(f"  Total time: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Estimate time remaining if printing
        if status.state == "printing" and status.progress > 0 and status.progress < 1.0:
            remaining = (status.print_duration / status.progress) - status.print_duration
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)
            console.print(f"  Remaining: ~{hours:02d}:{minutes:02d}:{seconds:02d}")

    # Show filament usage
    if status.filament_used > 0:
        filament_m = status.filament_used / 1000
        console.print(f"\n[dim]Filament:[/dim]")
        console.print(f"  Used: {filament_m:.2f} m")

    # Show message if present
    if status.message:
        console.print(f"\n[dim]Message:[/dim] {status.message}")


def _render_console_messages(messages: list[ConsoleMessage]) -> None:
    """Render list of console messages."""
    from datetime import datetime

    for msg in messages:
        dt = datetime.fromtimestamp(msg.time)
        time_str = dt.strftime("%H:%M:%S")

        # Color code by type
        if msg.type == "command":
            style = "cyan"
        elif msg.type == "error":
            style = "red"
        elif msg.type == "warning":
            style = "yellow"
        else:
            style = "white"

        console.print(f"[dim][{time_str}][/dim] [{style}]{msg.message}[/{style}]")


__all__ = ["render_result", "print_error", "print_warning", "console"]
