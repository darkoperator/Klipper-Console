#!/usr/bin/env python3
"""Test tab completion functionality."""

from klipper_console.moonraker import MoonrakerClient
from klipper_console.handlers import Handlers
from klipper_console.registry import CommandRegistry
from klipper_console.completion import KlipperCompleter
from prompt_toolkit.document import Document

def test_completions():
    """Test the completion system."""
    client = MoonrakerClient()
    client.connect()

    handlers = Handlers(client)
    registry = CommandRegistry(handlers)
    completer = KlipperCompleter(registry)

    # Test cases
    test_cases = [
        ("get_", "Command completion"),
        ("get_sensor ", "Sensor name completion"),
        ("get_sensor P", "Sensor name with prefix 'P'"),
        ("get_sensor ch", "Sensor name with prefix 'ch'"),
        ("get_fan ", "Fan name completion"),
        ("get_fan Bed", "Fan name with prefix 'Bed'"),
        ("set_fan BedFans ", "Parameter completion for set_fan"),
        ("set_fan BedFans S", "Parameter completion starting with 'S'"),
        ("set_led sb_leds ", "Parameter completion for set_led"),
        ("set_led sb_leds R", "Parameter completion starting with 'R'"),
        ("get_macro ", "Macro name completion"),
        ("get_macro PRINT", "Macro name with prefix 'PRINT'"),
    ]

    for text, description in test_cases:
        print(f"\n{description}:")
        print(f"  Input: '{text}'")

        # Create a document with the text
        doc = Document(text, len(text))

        # Get completions
        completions = list(completer.get_completions(doc, None))

        if completions:
            print(f"  Completions ({len(completions)}):")
            for comp in completions[:10]:  # Show first 10
                print(f"    - {comp.text}")
            if len(completions) > 10:
                print(f"    ... and {len(completions) - 10} more")
        else:
            print("  No completions")

    client.close()

if __name__ == "__main__":
    test_completions()
