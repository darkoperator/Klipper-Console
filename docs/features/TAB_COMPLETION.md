# Tab Completion Enhancement

## Overview

The console now features **context-aware tab completion** that suggests:
- Command names
- Component names (sensors, fans, LEDs, macros)
- Parameter names (SPEED=, RED=, etc.)

## How It Works

### 1. Command Completion

Type a partial command and press Tab:

```
klipper> get_<Tab>
```

Shows:
- get_fan
- get_led
- get_macro
- get_sensor

### 2. Component Name Completion

After typing a command, press Tab to see all available components:

```
klipper> get_sensor <Tab>
```

Shows all sensors:
- cartographer_coil
- Cartographer_MCU
- heater_bed
- Pi
- chamber
- NH36
- extruder

### 3. Filtered Completion

Type a prefix to filter results:

```
klipper> get_sensor ch<Tab>
```

Completes to:
```
klipper> get_sensor chamber
```

### 4. Parameter Completion

For set commands, get parameter suggestions:

```
klipper> set_fan BedFans <Tab>
```

Nothing shown (waiting for parameter name)

```
klipper> set_fan BedFans S<Tab>
```

Completes to:
```
klipper> set_fan BedFans SPEED=
```

## Implementation Details

### Caching Strategy

- Component lists are fetched from Moonraker on first use
- Lists are cached to avoid repeated API calls
- Cache includes:
  - All temperature sensors (with display names)
  - All fans (with display names)
  - All LEDs (with display names)
  - All macros

### Name Extraction

The completer automatically extracts display names by removing prefixes:
- `temperature_sensor chamber` → `chamber`
- `fan_generic BedFans` → `BedFans`
- `neopixel sb_leds` → `sb_leds`

Special cases like `heater_bed`, `extruder`, and `fan` (part cooling) are handled correctly.

### Supported Commands

**get_sensor**: Completes with sensor names
**get_fan**: Completes with fan names
**get_led**: Completes with LED names
**get_macro**: Completes with macro names
**set_fan**: Completes with fan names, then SPEED= parameter
**set_led**: Completes with LED names, then RED=, GREEN=, BLUE=, WHITE=, INDEX= parameters

## Testing

All completion scenarios tested with live printer:
- ✅ Command completion (4 get commands)
- ✅ Sensor completion (7 unique sensors)
- ✅ Fan completion (5 unique fans)
- ✅ LED completion (2 LEDs)
- ✅ Macro completion (61 macros)
- ✅ Parameter completion (SPEED=, RED=, etc.)
- ✅ Prefix filtering (chamber, BedFans, PRINT_START, etc.)

## User Experience

The tab completion makes the console highly discoverable:
- Users don't need to memorize component names
- Typing is faster with autocomplete
- Reduces typos and command errors
- Makes the console feel more polished and professional
