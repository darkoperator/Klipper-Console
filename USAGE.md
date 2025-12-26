# Klipper Console Usage Guide

## Starting the Console

```bash
./klipper-console.sh
```

Or directly:
```bash
./venv/bin/klipper-console
```

## Available Commands

### Help System
```
help                    # Show all commands
help <command>          # Show help for specific command
```

### Get Commands (Inspect State - Read Only)
Get commands return all items when called without arguments, or a specific item when a name is provided:

```
get_sensor              # Get all sensor states (table view)
get_sensor <name>       # Get specific sensor (e.g., get_sensor Pi)

get_fan                 # Get all fan states (table view)
get_fan <name>          # Get specific fan (e.g., get_fan BedFans)

get_led                 # Get all LED states
get_led <name>          # Get specific LED (e.g., get_led sb_leds)

get_heater              # Get all heater states (table view)
get_heater <name>       # Get specific heater (e.g., get_heater extruder)

get_pin                 # Get all output pin states
get_pin <name>          # Get specific pin (e.g., get_pin act_led)

get_macro               # List all G-code macros
get_macro <name>        # Get specific macro info
```

### Execution Commands

```
run                     # List all available macros
run <macro>             # Run a macro
run <macro> PARAM=val   # Run macro with parameters
  Examples:
    run status_ready                        # Run status_ready macro
    run PRINT_START BED_TEMP=60 EXTRUDER_TEMP=200   # Run with params
    run PARKFRONT                           # Park toolhead at front
    run Off                                 # Turn off LEDs (macro)
```

### Set Commands (Modify State - Write Operations)
```
set_fan <name> SPEED=<0.0-1.0>
  Examples:
    set_fan BedFans SPEED=0.5        # 50% speed
    set_fan pi_fan SPEED=1.0         # 100% speed
    set_fan controller_fan SPEED=0   # Off

set_led <name> RED=<0-1> GREEN=<0-1> BLUE=<0-1> [WHITE=<0-1>] [INDEX=<n>]
  Examples:
    set_led sb_leds RED=1 GREEN=0 BLUE=0           # Red
    set_led neopixel RED=0 GREEN=1 BLUE=0          # Green
    set_led neopixel RED=0 GREEN=0 BLUE=0          # Off
    set_led sb_leds RED=1 GREEN=1 BLUE=1 INDEX=1   # White, LED #1 only

set_heater <name> TEMP=<celsius>     **CAUTION: Controls physical heaters**
  Examples:
    set_heater extruder TEMP=200     # Set hotend to 200°C
    set_heater heater_bed TEMP=60    # Set bed to 60°C
    set_heater extruder TEMP=0       # Turn off hotend

set_pin <name> VALUE=<0.0-1.0>
  Examples:
    set_pin act_led VALUE=1.0        # Turn pin fully on
    set_pin act_led VALUE=0.5        # 50% PWM
    set_pin act_led VALUE=0          # Turn pin off
```

### Utility Commands
```
exit                    # Exit the console
quit                    # Exit the console
```

## Example Session

```
$ ./klipper-console.sh
Klipper Console
Type 'help' for available commands, 'exit' to quit.

klipper> get_sensor
                          Temperature Sensors
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Name              ┃ Temperature ┃    Min ┃     Max ┃ Target ┃ Power ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ cartographer_coil │      25.6°C │ 25.4°C │ 116.4°C │      - │     - │
│ Cartographer_MCU  │      39.5°C │ 37.0°C │ 100.9°C │      - │     - │
│ heater_bed        │      23.4°C │      - │       - │  0.0°C │    0% │
...

klipper> get_sensor chamber
chamber
  Temperature: 23.4°C
  Min: 23.4°C
  Max: 61.8°C

klipper> set_fan BedFans SPEED=0.5
Set BedFans speed to 0.5

klipper> get_fan BedFans
BedFans
  Speed: 50%

klipper> exit
Goodbye!
```

## Features

### Tab Completion
Press Tab at any point to get context-aware completions:

- **Commands**: `get_<Tab>` shows all get commands
- **Component Names**: `get_sensor <Tab>` shows all available sensors
- **Filtered Names**: `get_sensor ch<Tab>` completes to "chamber"
- **Parameters**: `set_fan BedFans S<Tab>` completes to "SPEED="
- **Macros**: `run <Tab>` shows all 61 macros
- **Filtered Macros**: `run PRINT<Tab>` shows PRINT_START, PRINT_END

Examples:
```
klipper> get_sen<Tab>           → get_sensor
klipper> get_sensor <Tab>       → shows: cartographer_coil, Cartographer_MCU, Pi, chamber, ...
klipper> get_sensor ch<Tab>     → get_sensor chamber
klipper> set_fan Bed<Tab>       → set_fan BedFans
klipper> set_fan BedFans S<Tab> → set_fan BedFans SPEED=
klipper> run <Tab>              → shows all 61 macros
klipper> run PRINT<Tab>         → shows: PRINT_START, PRINT_END
klipper> run status_<Tab>       → shows 10 status macros
```

### Other Features

- **Command History**: Use Up/Down arrows to navigate history
- **Auto-suggest**: Previously used commands are suggested as you type
- **Ctrl+C**: Cancel current line (doesn't exit)
- **Ctrl+D**: Exit the console
- **Rich Output**: Tables and colored output for easy reading

## Safety Notes

- All read commands (`get_*`) are safe and non-destructive
- Write commands (`set_*`) explicitly modify printer state
- **HEATER WARNING**: `set_heater` controls physical heating elements. Use with caution.
  - Always monitor temperatures when setting heater targets
  - Set to 0 to turn off heaters
  - Temperature limit is 0-300°C
- Pin commands control GPIO outputs - verify pin function before use
