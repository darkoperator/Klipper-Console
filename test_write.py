#!/usr/bin/env python3
"""Test write commands with live printer (safe components only)."""

import time
from klipper_console.moonraker import MoonrakerClient
from klipper_console.handlers import Handlers
from klipper_console.render import console

def main():
    client = MoonrakerClient()
    client.connect()

    handlers = Handlers(client)

    console.print("[bold yellow]Testing Write Commands (BedFans only)[/bold yellow]\n")

    # Get initial state
    console.print("[cyan]Initial BedFans state:[/cyan]")
    initial_fan = handlers.get_fan("BedFans")
    console.print(f"  Speed: {initial_fan.speed*100:.0f}%")

    # Test: Set to 25%
    console.print("\n[cyan]Setting BedFans to 25%...[/cyan]")
    handlers.set_fan_speed("BedFans", 0.25)
    time.sleep(0.5)
    fan = handlers.get_fan("BedFans")
    console.print(f"  Speed: {fan.speed*100:.0f}%")

    # Test: Set to 50%
    console.print("\n[cyan]Setting BedFans to 50%...[/cyan]")
    handlers.set_fan_speed("BedFans", 0.5)
    time.sleep(0.5)
    fan = handlers.get_fan("BedFans")
    console.print(f"  Speed: {fan.speed*100:.0f}%")

    # Restore to off
    console.print("\n[cyan]Restoring BedFans to 0%...[/cyan]")
    handlers.set_fan_speed("BedFans", 0.0)
    time.sleep(0.5)
    fan = handlers.get_fan("BedFans")
    console.print(f"  Speed: {fan.speed*100:.0f}%")

    console.print("\n[green]Write tests completed successfully![/green]")

    client.close()

if __name__ == "__main__":
    main()
