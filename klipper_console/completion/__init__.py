"""Tab completion for console commands."""

from prompt_toolkit.completion import Completer, Completion
from typing import Iterable, Optional


class KlipperCompleter(Completer):
    """Tab completion for Klipper console commands."""

    def __init__(self, registry):
        """Initialize with command registry."""
        self.registry = registry
        self.handlers = registry.handlers
        # Cache for component lists (refreshed periodically)
        self._cache = {}
        self._cache_valid = False

    def _refresh_cache(self):
        """Refresh cached component lists."""
        try:
            # Get sensors (extract display names)
            sensors = self.handlers.list_sensors()
            sensor_names = self._extract_names(sensors, [
                "temperature_sensor ", "temperature_host "
            ])
            # Remove duplicates while preserving order
            self._cache['sensors'] = list(dict.fromkeys(sensor_names))

            # Get fans (extract display names)
            fans = self.handlers.list_fans()
            fan_names = self._extract_names(fans, [
                "fan_generic ", "heater_fan ", "controller_fan "
            ])
            # Remove duplicates while preserving order
            self._cache['fans'] = list(dict.fromkeys(fan_names))

            # Get LEDs (extract display names)
            leds = self.handlers.list_leds()
            led_names = self._extract_names(leds, [
                "neopixel ", "led ", "dotstar "
            ])
            # Remove duplicates while preserving order
            self._cache['leds'] = list(dict.fromkeys(led_names))

            # Get macros
            self._cache['macros'] = self.handlers.list_macros()

            # Get heaters (no prefix extraction needed)
            heaters = self.handlers.list_heaters()
            self._cache['heaters'] = list(dict.fromkeys(heaters))

            # Get pins (extract display names)
            pins = self.handlers.list_pins()
            pin_names = self._extract_names(pins, ["output_pin "])
            self._cache['pins'] = list(dict.fromkeys(pin_names))

            # Get G-code commands
            self._cache['gcode_commands'] = self.handlers.list_gcode_commands()

            # Get G-code files (extract filenames from GCodeFile objects)
            gcode_files = self.handlers.list_gcode_files()
            self._cache['gcode_files'] = [f.filename for f in gcode_files]

            self._cache_valid = True
        except Exception:
            # If refresh fails, keep old cache or empty
            if not self._cache:
                self._cache = {
                    'sensors': [],
                    'fans': [],
                    'leds': [],
                    'macros': [],
                    'heaters': [],
                    'pins': [],
                    'gcode_commands': [],
                    'gcode_files': []
                }

    def _extract_names(self, full_names: list[str], prefixes: list[str]) -> list[str]:
        """Extract display names by removing prefixes."""
        names = []
        for full_name in full_names:
            name = full_name
            for prefix in prefixes:
                if full_name.startswith(prefix):
                    name = full_name.replace(prefix, "", 1)
                    break
            names.append(name)
        return names

    def _get_parameter_completions(self, command: str, current_word: str) -> list[str]:
        """Get parameter completions for a command."""
        params = []

        if command == "set_fan":
            params = ["SPEED="]
        elif command == "set_led":
            params = ["RED=", "GREEN=", "BLUE=", "WHITE=", "INDEX="]
        elif command == "set_heater":
            params = ["TEMP="]
        elif command == "set_pin":
            params = ["VALUE="]
        elif command == "extrude":
            params = ["AMOUNT=", "FEEDRATE="]

        return [p for p in params if p.startswith(current_word.upper())]

    def _get_local_file_completions(self, prefix: str, quote_char: str = '') -> list[tuple[str, str]]:
        """
        Get local file/directory completions for the current working directory.

        Args:
            prefix: The prefix to match (without quotes)
            quote_char: The quote character being used ('' for none, '"' or "'")

        Returns:
            List of tuples (completion_text, display_text)
        """
        import os
        from pathlib import Path

        try:
            # Get current working directory from registry
            cwd = self.registry._cwd

            # Handle path with directory separators
            if '/' in prefix:
                # Split into directory and filename parts
                dir_part = os.path.dirname(prefix)
                file_part = os.path.basename(prefix)

                # Resolve directory path
                if os.path.isabs(dir_part):
                    search_dir = dir_part
                else:
                    search_dir = os.path.join(cwd, dir_part)
            else:
                # Just a filename prefix, search in current directory
                search_dir = cwd
                file_part = prefix

            # Check if directory exists
            if not os.path.isdir(search_dir):
                return []

            # List files and directories
            items = []
            try:
                # Case-insensitive matching
                file_part_lower = file_part.lower()

                for item in os.listdir(search_dir):
                    if item.startswith('.') and not file_part.startswith('.'):
                        continue  # Skip hidden files unless explicitly requested

                    # Case-insensitive comparison
                    if item.lower().startswith(file_part_lower):
                        item_path = os.path.join(search_dir, item)
                        is_dir = os.path.isdir(item_path)

                        # Add directory indicator
                        display_name = item + '/' if is_dir else item

                        # Handle spaces in filenames
                        if ' ' in item:
                            # If not already quoted, add quotes
                            if not quote_char:
                                completion = f'"{item}{"/" if is_dir else ""}"'
                            else:
                                completion = display_name
                        else:
                            completion = display_name

                        items.append((completion, display_name))
            except PermissionError:
                pass

            return items
        except Exception:
            return []

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """Generate completions for the current input."""
        text = document.text_before_cursor
        words = text.split()

        # No input yet - show all commands
        if not words or (len(words) == 1 and not text.endswith(" ")):
            prefix = words[0] if words else ""
            for command in self.registry.get_commands():
                if command.startswith(prefix):
                    yield Completion(
                        command,
                        start_position=-len(prefix),
                        display=command,
                        display_meta=self.registry.get_command_help(command)
                    )
            return

        # We have at least one complete word (a command)
        command = words[0]

        # Refresh cache if needed (on first use or periodically)
        if not self._cache_valid:
            self._refresh_cache()

        # Special handling for local file path commands
        if command in ["upload_file", "ls", "cd"]:
            # Parse the argument considering quotes
            if len(words) == 1 and text.endswith(" "):
                prefix = ""
                quote_char = ''
            elif len(words) >= 2:
                # Get the portion after the command
                after_cmd = text[len(words[0]):].lstrip()

                # Check if we're inside quotes
                quote_char = ''
                if after_cmd.startswith('"'):
                    quote_char = '"'
                    prefix = after_cmd[1:]
                elif after_cmd.startswith("'"):
                    quote_char = "'"
                    prefix = after_cmd[1:]
                else:
                    prefix = words[1] if len(words) >= 2 and not text.endswith(" ") else ""
            else:
                return

            # Get local file completions
            local_files = self._get_local_file_completions(prefix, quote_char)
            for completion_text, display_text in local_files:
                yield Completion(
                    completion_text,
                    start_position=-len(prefix),
                    display=display_text
                )
            return

        # Second word - complete component names
        if len(words) == 1 and text.endswith(" "):
            # User just typed command + space, show all options for this command
            prefix = ""
        elif len(words) == 2 and not text.endswith(" "):
            # User is typing the second word
            prefix = words[1]
        else:
            # Third word or later - complete parameters
            if text.endswith(" "):
                # User typed space, show all parameters
                current_word = ""
            else:
                # User is typing, filter parameters
                current_word = words[-1]

            params = self._get_parameter_completions(command, current_word)
            for param in params:
                yield Completion(
                    param,
                    start_position=-len(current_word),
                    display=param
                )
            return

        # Get appropriate completion list based on command
        candidates = []
        if command == "home":
            # Complete axis names for home command
            candidates = ['X', 'Y', 'Z']
        elif command == "get_sensor":
            candidates = self._cache.get('sensors', [])
        elif command == "get_fan":
            candidates = self._cache.get('fans', [])
        elif command == "get_led":
            candidates = self._cache.get('leds', [])
        elif command == "get_macro":
            candidates = self._cache.get('macros', [])
        elif command == "get_heater":
            candidates = self._cache.get('heaters', [])
        elif command == "get_pin":
            candidates = self._cache.get('pins', [])
        elif command == "set_fan":
            candidates = self._cache.get('fans', [])
        elif command == "set_led":
            candidates = self._cache.get('leds', [])
        elif command == "set_heater":
            candidates = self._cache.get('heaters', [])
        elif command == "set_pin":
            candidates = self._cache.get('pins', [])
        elif command == "run":
            candidates = self._cache.get('macros', [])
        elif command == "get_gcode":
            candidates = self._cache.get('gcode_commands', [])
        elif command == "run_gcode":
            candidates = self._cache.get('gcode_commands', [])
        elif command == "get_file":
            candidates = self._cache.get('gcode_files', [])
        elif command == "delete_file":
            candidates = self._cache.get('gcode_files', [])
        elif command == "move_file":
            candidates = self._cache.get('gcode_files', [])
        elif command == "copy_file":
            candidates = self._cache.get('gcode_files', [])
        elif command == "print_file":
            candidates = self._cache.get('gcode_files', [])
        elif command == "download_file":
            candidates = self._cache.get('gcode_files', [])

        # Filter and yield completions (case-insensitive)
        prefix_lower = prefix.lower()
        for candidate in candidates:
            if candidate.lower().startswith(prefix_lower):
                # Handle files with spaces - add quotes if needed
                if ' ' in candidate:
                    completion_text = f'"{candidate}"'
                else:
                    completion_text = candidate

                yield Completion(
                    completion_text,
                    start_position=-len(prefix),
                    display=candidate
                )


__all__ = ["KlipperCompleter"]
