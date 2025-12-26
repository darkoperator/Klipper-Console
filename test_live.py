#!/usr/bin/env python3
"""Test script for live printer commands."""

from klipper_console.moonraker import MoonrakerClient
from klipper_console.handlers import Handlers
from klipper_console.render import render_result, console

def main():
    client = MoonrakerClient()
    client.connect()

    handlers = Handlers(client)

    console.print("[bold]Testing Klipper Console with Live Printer[/bold]\n")

    # Test 1: List and get sensors
    console.print("[cyan]Test 1: Temperature Sensors[/cyan]")
    sensors = handlers.get_all_sensors()
    render_result(sensors)

    # Test 2: List and get fans
    console.print("\n[cyan]Test 2: Fans[/cyan]")
    fans = handlers.get_all_fans()
    render_result(fans)

    # Test 3: List LEDs
    console.print("\n[cyan]Test 3: LEDs[/cyan]")
    leds = handlers.get_all_leds()
    render_result(leds)

    # Test 4: Get specific sensor
    console.print("\n[cyan]Test 4: Get Specific Sensor (chamber)[/cyan]")
    sensor = handlers.get_sensor("chamber")
    render_result(sensor)

    # Test 5: Get specific fan
    console.print("\n[cyan]Test 5: Get Specific Fan (pi_fan)[/cyan]")
    fan = handlers.get_fan("pi_fan")
    render_result(fan)

    console.print("\n[green]All tests passed![/green]")

    client.close()

if __name__ == "__main__":
    main()
