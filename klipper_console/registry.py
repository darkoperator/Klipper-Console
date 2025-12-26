"""Command registry and dispatcher."""

import os
from typing import Callable, Any, Optional
from .handlers import Handlers
from .parser import ParsedCommand


class CommandRegistry:
    """Registry for console commands."""

    def __init__(self, handlers: Handlers):
        """Initialize registry with handlers."""
        self.handlers = handlers
        self._commands: dict[str, Callable] = {}
        self._descriptions: dict[str, str] = {}
        self._cwd = os.getcwd()  # Track current working directory
        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """Register all built-in commands."""
        # Get commands (return all if no args, specific if name provided)
        self.register("get_sensor", self._get_sensor, "Get sensor(s): get_sensor [name]")
        self.register("get_fan", self._get_fan, "Get fan(s): get_fan [name]")
        self.register("get_led", self._get_led, "Get LED(s): get_led [name]")
        self.register("get_macro", self._get_macro, "Get macro(s): get_macro [name]")
        self.register("get_heater", self._get_heater, "Get heater(s): get_heater [name]")
        self.register("get_pin", self._get_pin, "Get pin(s): get_pin [name]")
        self.register("get_toolhead", self._get_toolhead, "Get toolhead status and homing state")
        self.register("get_endstops", self._get_endstops, "Get endstop status")
        self.register("get_status", self._get_status, "Get printer status")
        self.register("get_print_status", self._get_print_status, "Get current print job status")
        self.register("get_file", self._get_file,
            "Get file(s): get_file [flags] [pattern] or get_file <filename>\n"
            "  Flags: -t (time) -S (size) -n (name) -r (reverse)\n"
            "  Example: get_file -t *.gcode")
        self.register("console", self._console, "Enter interactive console viewer with real-time output")

        # Set commands
        self.register("set_fan", self._set_fan, "Set fan speed: set_fan <name> SPEED=<0.0-1.0>")
        self.register("set_led", self._set_led, "Set LED color: set_led <name> RED=<0-1> GREEN=<0-1> BLUE=<0-1> [WHITE=<0-1>] [INDEX=<n>]")
        self.register("set_heater", self._set_heater, "Set heater temp: set_heater <name> TEMP=<celsius> (CAUTION: Physical heater control)")
        self.register("set_pin", self._set_pin, "Set pin value: set_pin <name> VALUE=<0.0-1.0>")

        # G-code commands
        self.register("get_gcode", self._get_gcode, "Get G-code command(s): get_gcode [command]")
        self.register("run_gcode", self._run_gcode, "Run G-code: run_gcode <command> [params...]")

        # Execution commands
        self.register("run", self._run_macro, "Run macro: run <macro_name> [PARAM=value ...]")
        self.register("home", self._home, "Home axes: home [X] [Y] [Z] (no args = home all)")
        self.register("extrude", self._extrude, "Extrude filament: extrude AMOUNT=<mm> [FEEDRATE=<mm/min>]")

        # Local filesystem navigation
        self.register("pwd", self._pwd, "Show current local working directory")
        self.register("ls", self._ls,
            "List local files: ls [flags] [pattern]\n"
            "  Flags: -t (time) -S (size) -n (name) -r (reverse) -a (all/hidden)\n"
            "  Example: ls -t *.gcode")
        self.register("cd", self._cd, "Change local directory: cd <path>")

        # Directory operations
        self.register("mkdir", self._mkdir, "Create directory: mkdir <path>")
        self.register("list_dir", self._list_dir,
            "List directories: list_dir [flags] [pattern]\n"
            "  Flags: -t (time) -S (size) -n (name) -r (reverse)\n"
            "  Example: list_dir -t subfolder_*")

        # File operations
        self.register("delete_file", self._delete_file, "Delete G-code file: delete_file <filename>")
        self.register("move_file", self._move_file, "Move G-code file: move_file <source> <dest>")
        self.register("copy_file", self._copy_file, "Copy G-code file: copy_file <source> <dest>")
        self.register("print_file", self._print_file, "Print G-code file: print_file <filename>")

        # File transfer
        self.register("upload_file", self._upload_file,
            "Upload file: upload_file <local_path> [remote_path]")
        self.register("download_file", self._download_file,
            "Download file: download_file <remote_path> <local_path>")

        # Utility commands
        self.register("help", self._help, "Show available commands")
        self.register("exit", self._exit, "Exit the console")
        self.register("quit", self._exit, "Exit the console")

    def register(self, name: str, handler: Callable, description: str = ""):
        """Register a command."""
        self._commands[name] = handler
        if description:
            self._descriptions[name] = description

    def get_commands(self) -> list[str]:
        """Get list of registered command names."""
        return sorted(self._commands.keys())

    def get_command_help(self, command: str) -> Optional[str]:
        """Get help text for a command."""
        return self._descriptions.get(command)

    def execute(self, parsed: ParsedCommand) -> Any:
        """
        Execute a parsed command.

        Args:
            parsed: ParsedCommand object

        Returns:
            Command result

        Raises:
            KeyError: If command not found
        """
        handler = self._commands.get(parsed.command)
        if not handler:
            raise KeyError(f"Unknown command: {parsed.command}")

        return handler(parsed)

    # Get command handlers

    def _get_sensor(self, cmd: ParsedCommand) -> Any:
        """Get sensor state(s)."""
        if cmd.args:
            # Get specific sensor
            return self.handlers.get_sensor(cmd.args[0])
        else:
            # Get all sensors
            return self.handlers.get_all_sensors()

    def _get_fan(self, cmd: ParsedCommand) -> Any:
        """Get fan state(s)."""
        if cmd.args:
            # Get specific fan
            return self.handlers.get_fan(cmd.args[0])
        else:
            # Get all fans
            return self.handlers.get_all_fans()

    def _get_led(self, cmd: ParsedCommand) -> Any:
        """Get LED state(s)."""
        if cmd.args:
            # Get specific LED
            return self.handlers.get_led(cmd.args[0])
        else:
            # Get all LEDs
            return self.handlers.get_all_leds()

    def _get_macro(self, cmd: ParsedCommand) -> Any:
        """Get macro(s)."""
        if cmd.args:
            # Get detailed info about specific macro
            name = cmd.args[0]
            return self.handlers.get_macro(name)
        else:
            # Get all macros
            return self.handlers.list_macros()

    def _get_heater(self, cmd: ParsedCommand) -> Any:
        """Get heater state(s)."""
        if cmd.args:
            # Get specific heater
            return self.handlers.get_heater(cmd.args[0])
        else:
            # Get all heaters
            return self.handlers.get_all_heaters()

    def _get_pin(self, cmd: ParsedCommand) -> Any:
        """Get pin state(s)."""
        if cmd.args:
            # Get specific pin
            return self.handlers.get_pin(cmd.args[0])
        else:
            # Get all pins
            return self.handlers.get_all_pins()

    def _get_toolhead(self, cmd: ParsedCommand) -> Any:
        """Get toolhead status."""
        return self.handlers.get_toolhead()

    def _get_endstops(self, cmd: ParsedCommand) -> Any:
        """Get endstop status."""
        return self.handlers.get_endstops()

    def _get_status(self, cmd: ParsedCommand) -> Any:
        """Get printer status."""
        return self.handlers.get_printer_status()

    def _get_print_status(self, cmd: ParsedCommand) -> Any:
        """Get print job status."""
        return self.handlers.get_print_status()

    def _console(self, cmd: ParsedCommand) -> str:
        """Enter interactive console viewer."""
        from .console_viewer import ConsoleViewer

        split_screen = getattr(self.handlers, 'split_screen_enabled', False)
        viewer = ConsoleViewer(self.handlers, split_screen=split_screen)
        viewer.start()

        return "Exited console mode"

    def _get_file(self, cmd: ParsedCommand) -> Any:
        """
        Get file(s) with optional filtering and sorting.

        Supports shell-style parameters:
        - get_file              # list all, sorted by name
        - get_file -t           # sorted by time (newest first)
        - get_file -S           # sorted by size (largest first)
        - get_file -r           # reverse sort
        - get_file -t -r        # time sorted, oldest first
        - get_file *.gcode      # filter by pattern
        - get_file -S test_*    # pattern + size sort
        - get_file filename     # show specific file details
        """
        # Parse arguments into flags, patterns, and filename
        flags = []
        patterns = []
        filename = None

        for arg in cmd.args:
            if arg.startswith('-'):
                # Flag: extract characters after dash (supports -tr for -t -r)
                flags.extend(arg[1:])
            elif '*' in arg or '?' in arg or '[' in arg:
                # Wildcard pattern
                patterns.append(arg)
            else:
                # Specific filename for detail view
                filename = arg
                break

        # Show detailed info for specific file
        if filename and not patterns:
            return self.handlers.get_file_info(filename)

        # List files with full metadata
        files = self.handlers.list_gcode_files()

        # Apply wildcard filtering if patterns specified
        if patterns:
            import fnmatch
            filtered_files = []
            for file in files:
                for pattern in patterns:
                    if fnmatch.fnmatch(file.filename, pattern):
                        filtered_files.append(file)
                        break
            files = filtered_files

        # Determine sort type and direction
        sort_key = 'name'  # default
        reverse = False

        for flag in flags:
            if flag == 't':
                sort_key = 'time'
            elif flag == 'S':
                sort_key = 'size'
            elif flag == 'n':
                sort_key = 'name'
            elif flag == 'r':
                reverse = True
            else:
                raise ValueError(f"Unknown flag: -{flag}")

        # Apply sorting
        if sort_key == 'name':
            # Alphabetical (A-Z), case-insensitive
            files.sort(key=lambda f: f.filename.lower(), reverse=reverse)
        elif sort_key == 'time':
            # Newest first by default (reverse=not reverse to flip default)
            files.sort(key=lambda f: f.modified, reverse=not reverse)
        elif sort_key == 'size':
            # Largest first by default
            files.sort(key=lambda f: f.size, reverse=not reverse)

        return files

    # Set command handlers

    def _set_fan(self, cmd: ParsedCommand) -> str:
        """Set fan speed."""
        if not cmd.args:
            raise ValueError("Usage: set_fan <name> SPEED=<0.0-1.0>")

        name = cmd.args[0]
        if "SPEED" not in cmd.kwargs:
            raise ValueError("SPEED parameter required")

        speed = float(cmd.kwargs["SPEED"])
        self.handlers.set_fan_speed(name, speed)
        return f"Set {name} speed to {speed}"

    def _set_led(self, cmd: ParsedCommand) -> str:
        """Set LED color."""
        if not cmd.args:
            raise ValueError("Usage: set_led <name> RED=<0-1> GREEN=<0-1> BLUE=<0-1> [WHITE=<0-1>] [INDEX=<n>]")

        name = cmd.args[0]
        required_params = ["RED", "GREEN", "BLUE"]
        for param in required_params:
            if param not in cmd.kwargs:
                raise ValueError(f"{param} parameter required")

        red = float(cmd.kwargs["RED"])
        green = float(cmd.kwargs["GREEN"])
        blue = float(cmd.kwargs["BLUE"])
        white = float(cmd.kwargs.get("WHITE", "0.0"))
        index = int(cmd.kwargs["INDEX"]) if "INDEX" in cmd.kwargs else None

        self.handlers.set_led_color(name, red, green, blue, white, index)
        return f"Set {name} color to R={red} G={green} B={blue}"

    def _set_heater(self, cmd: ParsedCommand) -> str:
        """Set heater temperature."""
        if not cmd.args:
            raise ValueError("Usage: set_heater <name> TEMP=<celsius>")

        name = cmd.args[0]
        if "TEMP" not in cmd.kwargs:
            raise ValueError("TEMP parameter required")

        temp = float(cmd.kwargs["TEMP"])
        self.handlers.set_heater_temp(name, temp)
        return f"Set {name} target temperature to {temp}°C"

    def _set_pin(self, cmd: ParsedCommand) -> str:
        """Set pin value."""
        if not cmd.args:
            raise ValueError("Usage: set_pin <name> VALUE=<0.0-1.0>")

        name = cmd.args[0]
        if "VALUE" not in cmd.kwargs:
            raise ValueError("VALUE parameter required")

        value = float(cmd.kwargs["VALUE"])
        self.handlers.set_pin_value(name, value)
        return f"Set {name} to {value}"

    # G-code command handlers

    def _get_gcode(self, cmd: ParsedCommand) -> Any:
        """Get G-code command(s) help."""
        if cmd.args:
            # Get help for specific command
            return self.handlers.get_gcode_command(cmd.args[0])
        else:
            # List all commands
            return self.handlers.list_gcode_commands()

    def _run_gcode(self, cmd: ParsedCommand) -> str:
        """Run a G-code command."""
        if not cmd.args:
            # Show available commands
            commands = self.handlers.list_gcode_commands()
            if commands:
                result = ["Available G-code commands (use 'get_gcode <cmd>' for help):"]
                # Show first 20 commands
                for command in commands[:20]:
                    result.append(f"  {command}")
                if len(commands) > 20:
                    result.append(f"  ... and {len(commands) - 20} more")
                return "\n".join(result)
            else:
                return "No G-code commands available"

        command_name = cmd.args[0]

        # Build the G-code command with any additional arguments
        gcode_parts = [command_name]

        # Add additional positional args
        if len(cmd.args) > 1:
            gcode_parts.extend(cmd.args[1:])

        # Add keyword args
        for key, value in cmd.kwargs.items():
            gcode_parts.append(f"{key}={value}")

        gcode_command = " ".join(gcode_parts)

        # Execute via handlers
        result = self.handlers.gcode(gcode_command)

        if result:
            return result
        else:
            return f"Executed: {gcode_command}"

    # Execution command handlers

    def _run_macro(self, cmd: ParsedCommand) -> str:
        """Run a macro."""
        if not cmd.args:
            # Show available macros
            macros = self.handlers.list_macros()
            if macros:
                result = ["Available macros:"]
                result.extend(f"  {macro}" for macro in macros)
                return "\n".join(result)
            else:
                return "No macros available"

        macro_name = cmd.args[0]

        # Build the G-code command with parameters
        gcode_parts = [macro_name]
        for key, value in cmd.kwargs.items():
            gcode_parts.append(f"{key}={value}")

        gcode_command = " ".join(gcode_parts)

        # Execute via handlers
        result = self.handlers.gcode(gcode_command)

        if result:
            return result
        else:
            return f"Executed: {gcode_command}"

    def _home(self, cmd: ParsedCommand) -> str:
        """Home axes."""
        # Get axes from args (e.g., ['X', 'Y'] or empty for all)
        axes = [arg.upper() for arg in cmd.args if arg.upper() in ['X', 'Y', 'Z']]

        # Execute homing
        self.handlers.home_axes(axes)

        if axes:
            return f"Homing {', '.join(axes)}"
        else:
            return "Homing all axes"

    def _extrude(self, cmd: ParsedCommand) -> str:
        """Extrude filament."""
        if "AMOUNT" not in cmd.kwargs:
            raise ValueError("Usage: extrude AMOUNT=<mm> [FEEDRATE=<mm/min>]")

        amount = float(cmd.kwargs["AMOUNT"])
        feedrate = int(cmd.kwargs.get("FEEDRATE", "300"))

        # Execute extrusion
        self.handlers.extrude(amount, feedrate)

        action = "Extruding" if amount > 0 else "Retracting"
        return f"{action} {abs(amount)}mm at {feedrate}mm/min"

    # File operation handlers

    def _delete_file(self, cmd: ParsedCommand) -> str:
        """Delete a file."""
        if not cmd.args:
            raise ValueError("Usage: delete_file <filename>")

        filename = cmd.args[0]
        self.handlers.delete_gcode_file(filename)
        return f"Deleted: {filename}"

    def _move_file(self, cmd: ParsedCommand) -> str:
        """Move a file."""
        if len(cmd.args) < 2:
            raise ValueError("Usage: move_file <source> <dest>")

        source = cmd.args[0]
        dest = cmd.args[1]
        self.handlers.move_gcode_file(source, dest)
        return f"Moved: {source} -> {dest}"

    def _copy_file(self, cmd: ParsedCommand) -> str:
        """Copy a file."""
        if len(cmd.args) < 2:
            raise ValueError("Usage: copy_file <source> <dest>")

        source = cmd.args[0]
        dest = cmd.args[1]
        self.handlers.copy_gcode_file(source, dest)
        return f"Copied: {source} -> {dest}"

    def _print_file(self, cmd: ParsedCommand) -> str:
        """Print a file."""
        if not cmd.args:
            raise ValueError("Usage: print_file <filename>")

        filename = cmd.args[0]
        self.handlers.print_gcode_file(filename)
        return f"Starting print: {filename}"

    # Directory operation handlers

    def _mkdir(self, cmd: ParsedCommand) -> str:
        """Create a directory."""
        if not cmd.args:
            raise ValueError("Usage: mkdir <path>")

        path = cmd.args[0]
        return self.handlers.create_directory(path)

    def _list_dir(self, cmd: ParsedCommand) -> Any:
        """List directories with filtering and sorting."""
        import fnmatch

        # Parse flags and patterns (same logic as _get_file)
        flags = []
        patterns = []
        base_path = "gcodes"

        for arg in cmd.args:
            if arg.startswith('-'):
                flags.extend(arg[1:])
            elif '*' in arg or '?' in arg or '[' in arg:
                patterns.append(arg)
            else:
                base_path = arg

        # List directories
        directories = self.handlers.list_directories(base_path)

        # Apply wildcard filtering
        if patterns:
            filtered_dirs = []
            for directory in directories:
                for pattern in patterns:
                    if fnmatch.fnmatch(directory.dirname, pattern):
                        filtered_dirs.append(directory)
                        break
            directories = filtered_dirs

        # Apply sorting (same as files)
        sort_key = 'name'
        reverse = False

        for flag in flags:
            if flag == 't':
                sort_key = 'time'
            elif flag == 'S':
                sort_key = 'size'
            elif flag == 'n':
                sort_key = 'name'
            elif flag == 'r':
                reverse = True
            else:
                raise ValueError(f"Unknown flag: -{flag}")

        if sort_key == 'name':
            directories.sort(key=lambda d: d.dirname.lower(), reverse=reverse)
        elif sort_key == 'time':
            directories.sort(key=lambda d: d.modified, reverse=not reverse)
        elif sort_key == 'size':
            directories.sort(key=lambda d: d.size, reverse=not reverse)

        return directories

    # File transfer handlers

    def _upload_file(self, cmd: ParsedCommand) -> str:
        """Upload a file to the printer."""
        if not cmd.args:
            raise ValueError("Usage: upload_file <local_path> [remote_path]")

        local_path = cmd.args[0]
        remote_path = cmd.args[1] if len(cmd.args) > 1 else "gcodes"

        # Resolve local path relative to current working directory
        if not os.path.isabs(local_path):
            local_path = os.path.join(self._cwd, local_path)

        # Print status message
        from .render import console
        console.print(f"[yellow]Uploading {local_path}...[/yellow]")

        result = self.handlers.upload_file(local_path, remote_path)

        console.print("[green]Done[/green]")
        return result

    def _download_file(self, cmd: ParsedCommand) -> str:
        """Download a file from the printer."""
        if len(cmd.args) < 2:
            raise ValueError("Usage: download_file <remote_path> <local_path>")

        remote_path = cmd.args[0]
        local_path = cmd.args[1]

        # Resolve local path relative to current working directory
        if not os.path.isabs(local_path):
            local_path = os.path.join(self._cwd, local_path)

        # Print status message
        from .render import console
        console.print(f"[yellow]Downloading {remote_path}...[/yellow]")

        result = self.handlers.download_file(remote_path, local_path)

        console.print("[green]Done[/green]")
        return result

    # Local filesystem navigation handlers

    def _pwd(self, cmd: ParsedCommand) -> str:
        """Show current working directory."""
        return f"Local: {self._cwd}"

    def _cd(self, cmd: ParsedCommand) -> str:
        """Change current working directory."""
        if not cmd.args:
            # cd with no args goes to home directory
            self._cwd = os.path.expanduser("~")
            return f"Changed to: {self._cwd}"

        path = cmd.args[0]

        # Handle special cases
        if path == "~":
            path = os.path.expanduser("~")
        elif not os.path.isabs(path):
            # Relative path - resolve from current directory
            path = os.path.join(self._cwd, path)

        # Normalize path (resolve .., ., etc.)
        path = os.path.abspath(path)

        # Check if directory exists
        if not os.path.isdir(path):
            raise ValueError(f"Not a directory: {path}")

        self._cwd = path
        return f"Changed to: {self._cwd}"

    def _ls(self, cmd: ParsedCommand) -> list[str]:
        """
        List local files with filtering and sorting.

        Supports shell-style flags:
        - ls              # list current directory
        - ls -t           # sorted by time
        - ls -S           # sorted by size
        - ls -r           # reverse sort
        - ls -a           # include hidden files
        - ls *.gcode      # filter by pattern
        - ls /path        # list specific directory
        """
        import fnmatch
        from pathlib import Path

        # Parse flags, patterns, and path
        flags = []
        patterns = []
        target_path = self._cwd  # Default to current working directory

        for arg in cmd.args:
            if arg.startswith('-'):
                flags.extend(arg[1:])
            elif '*' in arg or '?' in arg or '[' in arg:
                patterns.append(arg)
            else:
                # It's a path
                if os.path.isabs(arg):
                    target_path = arg
                else:
                    target_path = os.path.join(self._cwd, arg)

        # Check if path exists
        if not os.path.isdir(target_path):
            raise ValueError(f"Not a directory: {target_path}")

        # List files
        try:
            all_items = os.listdir(target_path)
        except PermissionError:
            raise ValueError(f"Permission denied: {target_path}")

        # Filter hidden files unless -a flag
        show_hidden = 'a' in flags
        if not show_hidden:
            all_items = [item for item in all_items if not item.startswith('.')]

        # Build file info list
        files_info = []
        for item in all_items:
            item_path = os.path.join(target_path, item)
            try:
                stat = os.stat(item_path)
                files_info.append({
                    'name': item,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'is_dir': os.path.isdir(item_path)
                })
            except (OSError, PermissionError):
                # Skip files we can't stat
                continue

        # Apply pattern filtering
        if patterns:
            filtered_files = []
            for file_info in files_info:
                for pattern in patterns:
                    if fnmatch.fnmatch(file_info['name'], pattern):
                        filtered_files.append(file_info)
                        break
            files_info = filtered_files

        # Determine sort key
        sort_key = 'name'  # default
        reverse = False

        for flag in flags:
            if flag == 't':
                sort_key = 'time'
            elif flag == 'S':
                sort_key = 'size'
            elif flag == 'n':
                sort_key = 'name'
            elif flag == 'r':
                reverse = True
            elif flag == 'a':
                pass  # Already handled
            else:
                raise ValueError(f"Unknown flag: -{flag}")

        # Apply sorting
        if sort_key == 'name':
            files_info.sort(key=lambda f: f['name'].lower(), reverse=reverse)
        elif sort_key == 'time':
            files_info.sort(key=lambda f: f['modified'], reverse=not reverse)
        elif sort_key == 'size':
            files_info.sort(key=lambda f: f['size'], reverse=not reverse)

        # Format output (simple list with indicators for directories)
        result = []
        for file_info in files_info:
            name = file_info['name']
            if file_info['is_dir']:
                name = f"{name}/"  # Add trailing slash for directories
            result.append(name)

        return result if result else ["(empty directory)"]

    # Utility command handlers

    def _help(self, cmd: ParsedCommand) -> str:
        """Show help."""
        if cmd.args:
            # Help for specific command
            command = cmd.args[0]
            help_text = self.get_command_help(command)
            if help_text:
                return f"{command}: {help_text}"
            else:
                return f"No help available for: {command}"
        else:
            # List all commands
            lines = ["Available commands:"]
            for command in self.get_commands():
                help_text = self.get_command_help(command)
                if help_text:
                    # Handle multi-line help text with proper indentation
                    help_lines = help_text.split('\n')
                    # First line with command name
                    lines.append(f"  {command:20s} - {help_lines[0]}")
                    # Continuation lines indented to align with first line
                    # Indent = 2 (base) + 20 (command width) + 3 (" - ") = 25 spaces
                    for continuation in help_lines[1:]:
                        lines.append(f"  {' ':20s}   {continuation}")
                else:
                    lines.append(f"  {command}")
            return "\n".join(lines)

    def _exit(self, cmd: ParsedCommand) -> str:
        """Exit signal."""
        return "__EXIT__"
