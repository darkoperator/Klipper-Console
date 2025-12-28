# Heater and Pin Support Added

## New Commands

### Heater Commands

**get_heater** - Query heater states
```bash
klipper> get_heater              # Show all heaters (table)
klipper> get_heater extruder     # Show extruder only
klipper> get_heater heater_bed   # Show bed only
```

Output includes:
- Current temperature (°C)
- Target temperature (°C)
- Power output (%)
- Color coding: Yellow when heating, Green when at temp

**set_heater** - Set heater target temperature
```bash
klipper> set_heater extruder TEMP=200      # Heat hotend to 200°C
klipper> set_heater heater_bed TEMP=60     # Heat bed to 60°C
klipper> set_heater extruder TEMP=0        # Turn off hotend
```

Safety features:
- Temperature limited to 0-300°C
- Clear warning in help text
- Uses standard Klipper G-code (M104/M140)

### Pin Commands

**get_pin** - Query output pin states
```bash
klipper> get_pin              # Show all output pins (table)
klipper> get_pin act_led      # Show specific pin
```

**set_pin** - Set output pin value
```bash
klipper> set_pin act_led VALUE=1.0    # Full on
klipper> set_pin act_led VALUE=0.5    # 50% PWM
klipper> set_pin act_led VALUE=0      # Off
```

Value range: 0.0-1.0 (supports PWM for compatible pins)

## Tab Completion

Both commands support full tab completion:

```bash
klipper> get_heater <Tab>          # Shows: extruder, heater_bed
klipper> set_heater extruder T<Tab> # Completes to: TEMP=
klipper> get_pin <Tab>              # Shows: act_led
klipper> set_pin act_led V<Tab>     # Completes to: VALUE=
```

## Implementation Details

### Models
- **Heater**: name, temperature, target, power
- **Pin**: name, value

### Handlers
- `list_heaters()` - Finds extruder, heater_bed, heater_generic_*
- `list_pins()` - Finds output_pin_*
- `get_heater(name)` / `get_all_heaters()`
- `get_pin(name)` / `get_all_pins()`
- `set_heater_temp(name, target)` - Uses M104/M140/SET_HEATER_TEMPERATURE
- `set_pin_value(name, value)` - Uses SET_PIN

### Rendering
- **Heaters**: Table with color-coded temperatures
  - Yellow: Heating (>5°C below target)
  - Green: At temperature (within 5°C of target)
  - Normal: No target set
- **Pins**: Simple table with name and value

## Testing Results

Tested with live printer:
- ✅ get_heater: Shows extruder (25°C) and heater_bed (23°C)
- ✅ get_heater extruder: Shows individual heater
- ✅ get_pin: Shows act_led (0.00)
- ✅ get_pin act_led: Shows individual pin
- ✅ Tab completion working for heater/pin names
- ✅ Tab completion working for TEMP= and VALUE= parameters

## Safety Warnings

**IMPORTANT**: The `set_heater` command controls physical heating elements:
- Always monitor temperatures when heating
- Temperature limit enforced: 0-300°C
- Set TEMP=0 to turn heaters off
- Help text includes safety warning

Output pins can control various hardware - verify pin function before using set_pin.
