#!/bin/bash
# Demo script showing klipper-console capabilities

echo "=== Klipper Console Demo ==="
echo ""
echo "Running various commands to demonstrate the console..."
echo ""

./klipper-console.sh <<'EOF'
help
get_sensor
get_sensor chamber
get_fan
get_fan pi_fan
get_led
get_macro
exit
EOF
