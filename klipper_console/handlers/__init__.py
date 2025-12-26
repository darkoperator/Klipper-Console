"""Command handlers for printer operations."""

from typing import Any, Optional
from ..moonraker import MoonrakerClient
from ..models import TemperatureSensor, Fan, LED, Macro, Heater, Pin, GCodeCommand, Toolhead, Endstops, PrinterState, GCodeFile, ConsoleMessage


class Handlers:
    """Command handlers using Moonraker client."""

    def __init__(self, client: MoonrakerClient):
        """Initialize handlers with Moonraker client."""
        self.client = client

    # List commands (enumerate resources)

    def list_sensors(self) -> list[str]:
        """List all temperature sensors."""
        objects = self.client.list_objects()
        sensors = [
            obj for obj in objects
            if obj.startswith("temperature_sensor ")
            or obj.startswith("temperature_host ")
            or obj == "extruder"
            or obj == "heater_bed"
        ]
        return sensors

    def list_fans(self) -> list[str]:
        """List all fans."""
        objects = self.client.list_objects()
        fans = [
            obj for obj in objects
            if obj.startswith("fan_generic ")
            or obj.startswith("heater_fan ")
            or obj.startswith("controller_fan ")
            or obj == "fan"
        ]
        return fans

    def list_leds(self) -> list[str]:
        """List all LEDs and neopixels."""
        objects = self.client.list_objects()
        leds = [
            obj for obj in objects
            if obj.startswith("neopixel ")
            or obj.startswith("led ")
            or obj.startswith("dotstar ")
        ]
        return leds

    def list_macros(self) -> list[str]:
        """List all G-code macros."""
        objects = self.client.list_objects()
        macros = [
            obj.replace("gcode_macro ", "")
            for obj in objects
            if obj.startswith("gcode_macro ")
        ]
        return macros

    def get_macro(self, name: str) -> Macro:
        """
        Get detailed information about a macro.

        Args:
            name: Macro name

        Returns:
            Macro object with description and parameters
        """
        # Get the configfile which contains macro definitions
        result = self.client.query_objects({"configfile": None})
        config = result["status"].get("configfile", {})
        settings = config.get("settings", {})

        # Look for the macro in settings (case-insensitive)
        macro_key = f"gcode_macro {name.lower()}"
        if macro_key not in settings:
            # Try without gcode_macro prefix if user provided full name
            if name.lower().startswith("gcode_macro "):
                macro_key = name.lower()
                name = name.replace("gcode_macro ", "").replace("GCODE_MACRO ", "")
            else:
                raise ValueError(f"Macro not found: {name}")

        macro_config = settings.get(macro_key, {})

        # Extract description
        description = macro_config.get("description", None)

        # Extract parameters from gcode
        gcode = macro_config.get("gcode", "")
        parameters = self._extract_macro_parameters(gcode)

        return Macro(
            name=name,
            description=description,
            parameters=parameters,
            gcode=gcode if len(gcode) < 500 else gcode[:500] + "..."  # Truncate long gcode
        )

    def _extract_macro_parameters(self, gcode: str) -> list[str]:
        """Extract parameter names from macro gcode."""
        import re
        # Find all params.PARAMNAME references
        param_pattern = r'params\.([A-Z_][A-Z0-9_]*)'
        matches = re.findall(param_pattern, gcode)
        # Remove duplicates and sort
        return sorted(set(matches))

    def list_heaters(self) -> list[str]:
        """List all heaters."""
        objects = self.client.list_objects()
        heaters = [
            obj for obj in objects
            if obj == "extruder"
            or obj == "heater_bed"
            or (obj.startswith("extruder") and obj[8:].isdigit())  # extruder1, extruder2, etc.
            or obj.startswith("heater_generic ")
        ]
        return heaters

    def list_pins(self) -> list[str]:
        """List all output pins."""
        objects = self.client.list_objects()
        pins = [
            obj for obj in objects
            if obj.startswith("output_pin ")
        ]
        return pins

    # Get commands (inspect state)

    def get_sensor(self, name: str) -> TemperatureSensor:
        """
        Get temperature sensor state.

        Args:
            name: Sensor name (with or without prefix)

        Returns:
            TemperatureSensor object
        """
        # Add prefix if needed
        if not any(name.startswith(prefix) for prefix in ["temperature_sensor ", "temperature_host "]):
            if name not in ["extruder", "heater_bed"]:
                full_name = f"temperature_sensor {name}"
            else:
                full_name = name
        else:
            full_name = name

        result = self.client.query_objects({full_name: None})
        status = result["status"].get(full_name, {})

        return TemperatureSensor(
            name=name,
            temperature=status.get("temperature", 0.0),
            measured_min_temp=status.get("measured_min_temp"),
            measured_max_temp=status.get("measured_max_temp"),
            target=status.get("target"),
            power=status.get("power")
        )

    def get_all_sensors(self) -> list[TemperatureSensor]:
        """Get all temperature sensor states."""
        sensor_names = self.list_sensors()
        if not sensor_names:
            return []

        # Query all sensors at once
        query_dict = {name: None for name in sensor_names}
        result = self.client.query_objects(query_dict)
        status = result["status"]

        sensors = []
        for full_name in sensor_names:
            data = status.get(full_name, {})
            # Extract display name
            if full_name.startswith("temperature_sensor "):
                display_name = full_name.replace("temperature_sensor ", "")
            elif full_name.startswith("temperature_host "):
                display_name = full_name.replace("temperature_host ", "")
            else:
                display_name = full_name

            sensors.append(TemperatureSensor(
                name=display_name,
                temperature=data.get("temperature", 0.0),
                measured_min_temp=data.get("measured_min_temp"),
                measured_max_temp=data.get("measured_max_temp"),
                target=data.get("target"),
                power=data.get("power")
            ))

        return sensors

    def get_fan(self, name: str) -> Fan:
        """
        Get fan state.

        Args:
            name: Fan name (with or without prefix)

        Returns:
            Fan object
        """
        # Add prefix if needed
        if name == "fan":
            full_name = "fan"
        elif not any(name.startswith(prefix) for prefix in ["fan_generic ", "heater_fan ", "controller_fan "]):
            full_name = f"fan_generic {name}"
        else:
            full_name = name

        result = self.client.query_objects({full_name: None})
        status = result["status"].get(full_name, {})

        return Fan(
            name=name,
            speed=status.get("speed", 0.0),
            rpm=status.get("rpm")
        )

    def get_all_fans(self) -> list[Fan]:
        """Get all fan states."""
        fan_names = self.list_fans()
        if not fan_names:
            return []

        query_dict = {name: None for name in fan_names}
        result = self.client.query_objects(query_dict)
        status = result["status"]

        fans = []
        for full_name in fan_names:
            data = status.get(full_name, {})
            # Extract display name
            if full_name.startswith("fan_generic "):
                display_name = full_name.replace("fan_generic ", "")
            elif full_name.startswith("heater_fan "):
                display_name = full_name.replace("heater_fan ", "")
            elif full_name.startswith("controller_fan "):
                display_name = full_name.replace("controller_fan ", "")
            else:
                display_name = full_name

            fans.append(Fan(
                name=display_name,
                speed=data.get("speed", 0.0),
                rpm=data.get("rpm")
            ))

        return fans

    def get_led(self, name: str) -> LED:
        """
        Get LED state.

        Args:
            name: LED name (with or without prefix)

        Returns:
            LED object
        """
        # Add prefix if needed
        if not any(name.startswith(prefix) for prefix in ["neopixel ", "led ", "dotstar "]):
            full_name = f"neopixel {name}"
        else:
            full_name = name

        result = self.client.query_objects({full_name: None})
        status = result["status"].get(full_name, {})

        return LED(
            name=name,
            color_data=status.get("color_data")
        )

    def get_all_leds(self) -> list[LED]:
        """Get all LED states."""
        led_names = self.list_leds()
        if not led_names:
            return []

        query_dict = {name: None for name in led_names}
        result = self.client.query_objects(query_dict)
        status = result["status"]

        leds = []
        for full_name in led_names:
            data = status.get(full_name, {})
            # Extract display name
            if full_name.startswith("neopixel "):
                display_name = full_name.replace("neopixel ", "")
            elif full_name.startswith("led "):
                display_name = full_name.replace("led ", "")
            elif full_name.startswith("dotstar "):
                display_name = full_name.replace("dotstar ", "")
            else:
                display_name = full_name

            leds.append(LED(
                name=display_name,
                color_data=data.get("color_data")
            ))

        return leds

    def get_heater(self, name: str) -> Heater:
        """
        Get heater state.

        Args:
            name: Heater name

        Returns:
            Heater object
        """
        # Heaters don't usually have prefixes - extruder, heater_bed, or heater_generic <name>
        if name in ["extruder", "heater_bed"] or name.startswith("extruder") or name.startswith("heater_generic "):
            full_name = name
        else:
            full_name = f"heater_generic {name}"

        result = self.client.query_objects({full_name: None})
        status = result["status"].get(full_name, {})

        return Heater(
            name=name,
            temperature=status.get("temperature", 0.0),
            target=status.get("target", 0.0),
            power=status.get("power", 0.0)
        )

    def get_all_heaters(self) -> list[Heater]:
        """Get all heater states."""
        heater_names = self.list_heaters()
        if not heater_names:
            return []

        query_dict = {name: None for name in heater_names}
        result = self.client.query_objects(query_dict)
        status = result["status"]

        heaters = []
        for full_name in heater_names:
            data = status.get(full_name, {})
            # Extract display name
            if full_name.startswith("heater_generic "):
                display_name = full_name.replace("heater_generic ", "")
            else:
                display_name = full_name

            heaters.append(Heater(
                name=display_name,
                temperature=data.get("temperature", 0.0),
                target=data.get("target", 0.0),
                power=data.get("power", 0.0)
            ))

        return heaters

    def get_pin(self, name: str) -> Pin:
        """
        Get output pin state.

        Args:
            name: Pin name (with or without prefix)

        Returns:
            Pin object
        """
        # Add prefix if needed
        if not name.startswith("output_pin "):
            full_name = f"output_pin {name}"
        else:
            full_name = name

        result = self.client.query_objects({full_name: None})
        status = result["status"].get(full_name, {})

        return Pin(
            name=name.replace("output_pin ", ""),
            value=status.get("value", 0.0)
        )

    def get_all_pins(self) -> list[Pin]:
        """Get all output pin states."""
        pin_names = self.list_pins()
        if not pin_names:
            return []

        query_dict = {name: None for name in pin_names}
        result = self.client.query_objects(query_dict)
        status = result["status"]

        pins = []
        for full_name in pin_names:
            data = status.get(full_name, {})
            display_name = full_name.replace("output_pin ", "")

            pins.append(Pin(
                name=display_name,
                value=data.get("value", 0.0)
            ))

        return pins

    # Set commands (write operations)

    def set_fan_speed(self, name: str, speed: float) -> None:
        """
        Set fan speed.

        Args:
            name: Fan name
            speed: Speed value 0.0-1.0
        """
        if not 0.0 <= speed <= 1.0:
            raise ValueError(f"Fan speed must be between 0.0 and 1.0, got {speed}")

        # Determine the correct G-code command
        if name == "fan" or name == "part_cooling":
            # Part cooling fan uses M106/M107
            if speed == 0:
                self.client.run_gcode("M107")
            else:
                s_value = int(speed * 255)
                self.client.run_gcode(f"M106 S{s_value}")
        else:
            # Generic fans use SET_FAN_SPEED
            self.client.run_gcode(f"SET_FAN_SPEED FAN={name} SPEED={speed}")

    def set_led_color(self, name: str, red: float, green: float, blue: float, white: float = 0.0, index: Optional[int] = None) -> None:
        """
        Set LED color.

        Args:
            name: LED name
            red: Red value 0.0-1.0
            green: Green value 0.0-1.0
            blue: Blue value 0.0-1.0
            white: White value 0.0-1.0 (for RGBW)
            index: Optional LED index (for strips)
        """
        for val, color_name in [(red, "red"), (green, "green"), (blue, "blue"), (white, "white")]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{color_name} must be between 0.0 and 1.0, got {val}")

        cmd_parts = [f"SET_LED LED={name}"]
        cmd_parts.append(f"RED={red}")
        cmd_parts.append(f"GREEN={green}")
        cmd_parts.append(f"BLUE={blue}")
        if white > 0:
            cmd_parts.append(f"WHITE={white}")
        if index is not None:
            cmd_parts.append(f"INDEX={index}")

        self.client.run_gcode(" ".join(cmd_parts))

    def set_heater_temp(self, name: str, target: float) -> None:
        """
        Set heater target temperature.

        Args:
            name: Heater name
            target: Target temperature in Celsius

        SAFETY WARNING: This controls physical heaters. Use with caution.
        """
        if target < 0 or target > 300:
            raise ValueError(f"Temperature must be between 0 and 300°C, got {target}")

        # Determine the correct G-code command
        if name == "extruder" or name == "hotend":
            self.client.run_gcode(f"M104 S{target}")
        elif name == "heater_bed" or name == "bed":
            self.client.run_gcode(f"M140 S{target}")
        else:
            # Generic heater
            self.client.run_gcode(f"SET_HEATER_TEMPERATURE HEATER={name} TARGET={target}")

    def set_pin_value(self, name: str, value: float) -> None:
        """
        Set output pin value.

        Args:
            name: Pin name
            value: Pin value (0.0-1.0 for PWM pins, 0 or 1 for digital)
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Pin value must be between 0.0 and 1.0, got {value}")

        self.client.run_gcode(f"SET_PIN PIN={name} VALUE={value}")

    # G-code commands

    def list_gcode_commands(self) -> list[str]:
        """List all available G-code commands."""
        help_dict = self.client.get_gcode_help()
        return sorted(help_dict.keys())

    def get_gcode_command(self, name: str) -> GCodeCommand:
        """
        Get help information for a specific G-code command.

        Args:
            name: Command name (case-insensitive)

        Returns:
            GCodeCommand object with name and description
        """
        help_dict = self.client.get_gcode_help()

        # Try exact match first
        if name in help_dict:
            return GCodeCommand(name=name, description=help_dict[name])

        # Try case-insensitive match
        name_upper = name.upper()
        for cmd_name, description in help_dict.items():
            if cmd_name.upper() == name_upper:
                return GCodeCommand(name=cmd_name, description=description)

        raise ValueError(f"G-code command not found: {name}")

    def gcode(self, command: str) -> str:
        """
        Execute raw G-code command.

        Args:
            command: G-code command to execute

        Returns:
            Command output
        """
        result = self.client.run_gcode(command)
        return str(result)

    # Toolhead and homing

    def get_toolhead(self) -> Toolhead:
        """
        Get toolhead status including homing state.

        Returns:
            Toolhead object with homing status and position
        """
        result = self.client.query_objects({"toolhead": None})
        status = result["status"].get("toolhead", {})

        return Toolhead(
            homed_axes=status.get("homed_axes", ""),
            position=status.get("position", [0.0, 0.0, 0.0, 0.0]),
            print_time=status.get("print_time", 0.0),
            estimated_print_time=status.get("estimated_print_time", 0.0)
        )

    def home_axes(self, axes: list[str]) -> None:
        """
        Home specified axes.

        Args:
            axes: List of axes to home (e.g., ['X', 'Y'] or empty list for all)
        """
        if not axes:
            # Home all axes
            self.client.run_gcode("G28")
        else:
            # Home specific axes
            axes_str = " ".join(axes)
            self.client.run_gcode(f"G28 {axes_str}")

    def get_endstops(self) -> Endstops:
        """
        Get endstop status.

        Returns:
            Endstops object with status of all endstops
        """
        result = self.client.get_endstops()
        return Endstops(endstops=result)

    def extrude(self, amount: float, feedrate: int = 300) -> None:
        """
        Extrude or retract filament.

        Args:
            amount: Amount to extrude in mm (negative to retract)
            feedrate: Feedrate in mm/min (default: 300)

        Note: Uses relative positioning for extrusion
        """
        if amount == 0:
            raise ValueError("Extrude amount cannot be zero")

        # Use relative positioning for extrusion
        self.client.run_gcode("M83")  # Set extruder to relative mode
        self.client.run_gcode(f"G1 E{amount} F{feedrate}")
        self.client.run_gcode("M82")  # Set extruder back to absolute mode

    # Printer status

    def get_printer_status(self) -> PrinterState:
        """
        Get printer status.

        Returns:
            PrinterState object with state and message
        """
        info = self.client.get_printer_info()
        return PrinterState(
            state=info.get("state", "unknown"),
            state_message=info.get("state_message", "")
        )

    def get_print_status(self):
        """
        Get current print job status.

        Returns:
            PrintStatus object with detailed print information
        """
        from ..models import PrintStatus

        # Query print_stats and virtual_sdcard objects
        result = self.client.query_objects({
            "print_stats": None,
            "virtual_sdcard": None
        })

        status = result.get("status", {})
        print_stats = status.get("print_stats", {})
        virtual_sdcard = status.get("virtual_sdcard", {})

        return PrintStatus(
            state=print_stats.get("state", "standby"),
            filename=print_stats.get("filename", ""),
            total_duration=print_stats.get("total_duration", 0.0),
            print_duration=print_stats.get("print_duration", 0.0),
            filament_used=print_stats.get("filament_used", 0.0),
            progress=virtual_sdcard.get("progress", 0.0),
            message=print_stats.get("message", "")
        )

    def get_console_history(self, count: int = 100) -> list[ConsoleMessage]:
        """
        Get historical console messages.

        Args:
            count: Number of messages to retrieve (default: 100)

        Returns:
            List of ConsoleMessage objects
        """
        import time

        messages = self.client.get_gcode_store(count)

        console_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                console_messages.append(ConsoleMessage(
                    message=msg.get("message", ""),
                    time=msg.get("time", time.time()),
                    type=msg.get("type", "response")
                ))
            elif isinstance(msg, str):
                # Handle simple string format
                console_messages.append(ConsoleMessage(
                    message=msg,
                    time=time.time(),
                    type="response"
                ))

        return console_messages

    # File management

    def list_gcode_files(self) -> list[GCodeFile]:
        """
        List all G-code files with full metadata.

        Returns:
            List of GCodeFile objects with path, size, and modified time
        """
        result = self.client.list_files("gcodes")

        # Handle both possible response formats
        if isinstance(result, list):
            files_data = result
        elif isinstance(result, dict) and "files" in result:
            files_data = result["files"]
        else:
            return []

        # Build GCodeFile objects with metadata
        files = []
        for item in files_data:
            if "path" not in item:
                continue
            files.append(GCodeFile(
                filename=item["path"],
                size=item.get("size", 0),
                modified=item.get("modified", 0.0),
                estimated_time=item.get("estimated_time"),
                filament_total=item.get("filament_total"),
            ))

        return files

    def get_file_info(self, filename: str) -> GCodeFile:
        """
        Get detailed information about a G-code file.

        Args:
            filename: File name

        Returns:
            GCodeFile object with metadata
        """
        metadata = self.client.get_file_metadata(filename)

        return GCodeFile(
            filename=metadata.get("filename", filename),
            size=metadata.get("size", 0),
            modified=metadata.get("modified", 0.0),
            estimated_time=metadata.get("estimated_time"),
            filament_total=metadata.get("filament_total"),
            first_layer_height=metadata.get("first_layer_height"),
            layer_height=metadata.get("layer_height"),
            object_height=metadata.get("object_height"),
            slicer=metadata.get("slicer"),
            thumbnails=metadata.get("thumbnails")
        )

    def delete_gcode_file(self, filename: str) -> None:
        """
        Delete a G-code file.

        Args:
            filename: File name to delete
        """
        self.client.delete_file(filename)

    def move_gcode_file(self, source: str, dest: str) -> None:
        """
        Move a G-code file.

        Args:
            source: Source file name
            dest: Destination file name
        """
        self.client.move_file(source, dest)

    def copy_gcode_file(self, source: str, dest: str) -> None:
        """
        Copy a G-code file.

        Args:
            source: Source file name
            dest: Destination file name
        """
        self.client.copy_file(source, dest)

    def print_gcode_file(self, filename: str) -> None:
        """
        Start printing a G-code file.

        Args:
            filename: File name to print
        """
        self.client.start_print(filename)

    # Directory management

    def create_directory(self, path: str) -> str:
        """
        Create a new directory.

        Args:
            path: Directory path

        Returns:
            Success message
        """
        # Ensure path starts with gcodes/ if not provided
        if not path.startswith("gcodes/") and not path.startswith("config/"):
            path = f"gcodes/{path}"

        result = self.client.create_directory(path)
        return f"Created directory: {result.get('item', {}).get('path', path)}"

    def list_directories(self, path: str = "gcodes") -> list:
        """
        List directories in the specified path.

        Args:
            path: Directory path (default: "gcodes")

        Returns:
            List of Directory objects
        """
        from ..models import Directory

        result = self.client.list_directory(path, extended=True)

        dirs_data = result.get("dirs", [])
        directories = []

        for dir_item in dirs_data:
            directories.append(Directory(
                dirname=dir_item.get("dirname", ""),
                size=dir_item.get("size", 0),
                modified=dir_item.get("modified", 0.0),
                permissions=dir_item.get("permissions")
            ))

        return directories

    # File upload/download

    def upload_file(self, local_path: str, remote_path: str = "gcodes") -> str:
        """
        Upload a file to the printer.

        Args:
            local_path: Local file path
            remote_path: Remote directory path (default: "gcodes")

        Returns:
            Success message
        """
        result = self.client.upload_file(local_path, remote_path)
        return f"Uploaded: {local_path} -> {result.get('item', {}).get('path', remote_path)}"

    def download_file(self, remote_path: str, local_path: str) -> str:
        """
        Download a file from the printer.

        Args:
            remote_path: Remote file path
            local_path: Local destination path

        Returns:
            Success message
        """
        self.client.download_file(remote_path, local_path)
        return f"Downloaded: {remote_path} -> {local_path}"


__all__ = ["Handlers"]
