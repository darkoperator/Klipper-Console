#!/bin/bash
# Final comprehensive test of klipper-console

echo "=== Final Klipper Console Test ==="
echo ""

../../klipper-console.sh <<'EOF'
# Test help
help

# Test get commands (all items)
get_sensor
get_fan
get_led
get_macro

# Test get commands (specific items)
get_sensor chamber
get_fan pi_fan
get_led sb_leds

# Test set command (safe fan control)
set_fan BedFans SPEED=0.2
get_fan BedFans
set_fan BedFans SPEED=0
get_fan BedFans

exit
EOF

echo ""
echo "=== Test Complete ==="
