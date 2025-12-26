"""Command parsing logic."""

import shlex
from typing import Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Parsed command structure."""
    command: str
    args: list[str]
    kwargs: dict[str, str]


def parse_command(line: str) -> Optional[ParsedCommand]:
    """
    Parse a command line into command, args, and kwargs.

    Args:
        line: Raw command line string

    Returns:
        ParsedCommand or None if empty

    Examples:
        >>> parse_command("list_sensors")
        ParsedCommand(command='list_sensors', args=[], kwargs={})

        >>> parse_command("get_sensor Pi")
        ParsedCommand(command='get_sensor', args=['Pi'], kwargs={})

        >>> parse_command("set_fan BedFans SPEED=0.5")
        ParsedCommand(command='set_fan', args=['BedFans'], kwargs={'SPEED': '0.5'})
    """
    line = line.strip()
    if not line:
        return None

    try:
        tokens = shlex.split(line)
    except ValueError:
        # If shlex fails (unclosed quotes), split on whitespace
        tokens = line.split()

    if not tokens:
        return None

    command = tokens[0]
    args = []
    kwargs = {}

    for token in tokens[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            kwargs[key] = value
        else:
            args.append(token)

    return ParsedCommand(command=command, args=args, kwargs=kwargs)
