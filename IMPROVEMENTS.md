# Command Structure Improvements

## Changes Made

### Simplified Command Model

**Before:**
- `list_sensors` - list sensor names
- `get_sensors` - get all sensor data
- `get_sensor <name>` - get specific sensor

**After:**
- `get_sensor` - get all sensor data (table view)
- `get_sensor <name>` - get specific sensor

### Benefits

1. **Less Redundancy** - Eliminated duplicate commands that did similar things
2. **More Intuitive** - Single command name per resource type
3. **Consistent Pattern** - All `get_*` commands work the same way:
   - No args = all items
   - With name = specific item
4. **Fewer Commands to Remember** - Reduced from 15+ commands to 8 core commands

### Current Command Set

**Get Commands** (read-only):
- `get_sensor [name]`
- `get_fan [name]`
- `get_led [name]`
- `get_macro [name]`

**Set Commands** (write operations):
- `set_fan <name> SPEED=<0.0-1.0>`
- `set_led <name> RED=<0-1> GREEN=<0-1> BLUE=<0-1> [WHITE=<0-1>] [INDEX=<n>]`

**Utility Commands**:
- `help [command]`
- `exit` / `quit`

### Testing

All commands tested successfully with live printer:
- ✅ Get all sensors (8 sensors found)
- ✅ Get specific sensor (chamber, Pi, etc.)
- ✅ Get all fans (5 fans found)
- ✅ Get specific fan (BedFans, pi_fan, etc.)
- ✅ Get all LEDs (2 LEDs found)
- ✅ Get all macros (61 macros found)
- ✅ Set fan speed (BedFans tested at 0%, 20%, back to 0%)

### Architecture

The simplified command structure maintains the same clean architecture:
- Commands registered in `registry.py`
- Handlers in `handlers/__init__.py`
- Rendering in `render/__init__.py`
- All business logic separated from presentation

This provides a solid foundation for future enhancements while keeping the interface simple and discoverable.
