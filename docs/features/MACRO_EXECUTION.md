# Macro Execution Support

## Overview

The console provides a `run` command to execute Klipper macros with full parameter support and tab completion.

## Commands

### List Macros

```bash
klipper> run
Available macros:
  _BEDFANVARS
  BEDFANSSLOW
  BEDFANSFAST
  BEDFANSOFF
  ...
  (61 total macros)
```

Or use:
```bash
klipper> get_macro              # Also lists all macros
```

### Run a Macro

Basic syntax:
```bash
klipper> run <macro_name>
```

With parameters:
```bash
klipper> run <macro_name> PARAM1=value PARAM2=value
```

## Examples

### Simple Macros (No Parameters)

```bash
klipper> run status_ready       # Set status LEDs to ready
klipper> run status_printing    # Set status LEDs to printing
klipper> run PARKFRONT          # Park toolhead at front
klipper> run PARKCENTER         # Park toolhead at center
klipper> run Off                # Turn off LEDs
klipper> run Green              # Set LEDs to green
```

### Macros with Parameters

```bash
klipper> run PRINT_START BED_TEMP=60 EXTRUDER_TEMP=200
klipper> run M109 S=200         # Wait for hotend temp
klipper> run M190 S=60          # Wait for bed temp
```

### LED Control Macros

Your printer has several LED control macros:
```bash
klipper> run Red                # Set LEDs to red
klipper> run Green              # Set LEDs to green
klipper> run Blue               # Set LEDs to blue
klipper> run Purple             # Set LEDs to purple
klipper> run White              # Set LEDs to white
klipper> run Off                # Turn off LEDs
```

### Status Macros

```bash
klipper> run status_off         # Turn off status LEDs
klipper> run status_ready       # Ready status
klipper> run status_busy        # Busy status
klipper> run status_heating     # Heating status
klipper> run status_leveling    # Leveling status
klipper> run status_homing      # Homing status
klipper> run status_printing    # Printing status
```

## Tab Completion

Full tab completion support for macro names:

```bash
klipper> run <Tab>              # Shows all 61 macros
klipper> run PRINT<Tab>         # Completes to PRINT_START or PRINT_END
klipper> run status_<Tab>       # Shows all 10 status_ macros
klipper> run PARK<Tab>          # Shows PARKFRONT, PARKFRONTLOW, PARKREAR, etc.
```

## Implementation Details

### How It Works

1. **Macro Discovery**: Macros are discovered from Klipper via Moonraker's object list
2. **Name Extraction**: `gcode_macro` prefix is automatically removed
3. **G-code Execution**: `run` forwards the macro name and parameters to Klipper as G-code
4. **Parameter Passing**: Parameters are passed in `KEY=value` format

### Behind the Scenes

When you run:
```bash
klipper> run PRINT_START BED_TEMP=60 EXTRUDER_TEMP=200
```

The console executes:
```gcode
PRINT_START BED_TEMP=60 EXTRUDER_TEMP=200
```

This is sent directly to Klipper via Moonraker's G-code execution endpoint.

### Available on Your Printer

Your printer has 61 macros including:
- **Bed fans**: BEDFANSSLOW, BEDFANSFAST, BEDFANSOFF
- **Heating**: M109, M190, M140, TURN_OFF_HEATERS
- **LEDs**: Red, Green, Blue, Purple, White, Off, status_*
- **Parking**: PARKFRONT, PARKFRONTLOW, PARKREAR, PARKCENTER, PARKBED
- **Print control**: PRINT_START, PRINT_END, PAUSE, RESUME, CANCEL_PRINT
- **Filament**: LOAD_FILAMENT, UNLOAD_FILAMENT, HOT_LOAD, HOT_UNLOAD, M600
- **Maintenance**: clean_nozzle, DUMP_PARAMETERS, HOME, G32

## Comparison: run vs Direct Macro Commands

**With `run` command (implemented):**
```bash
klipper> run PRINT_START BED_TEMP=60
klipper> run status_ready
```

Benefits:
- ✅ Clean namespace (61 macros don't clutter main commands)
- ✅ Clear execution intent (`run` makes it obvious)
- ✅ Easy parameter passing
- ✅ Tab completion shows all macros after `run `
- ✅ Can list all macros with just `run`

**Alternative: Direct commands (NOT implemented):**
```bash
klipper> PRINT_START BED_TEMP=60
klipper> status_ready
```

Drawbacks:
- ❌ 61 macros pollute command list
- ❌ Help command becomes cluttered
- ❌ Less clear distinction between built-in and macro commands
- ❌ Tab completion less useful with 70+ top-level commands

The `run` command approach provides better discoverability and organization.
