#!/bin/bash
# Wrapper script to run klipper-console from venv
cd "$(dirname "$0")"
exec ./venv/bin/klipper-console "$@"
