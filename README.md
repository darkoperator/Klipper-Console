# Klipper Console

A powerful, terminal-native CLI for controlling and monitoring Klipper 3D printers via Moonraker.

Klipper Console provides an SSH-friendly REPL with advanced discoverability, comprehensive file management, real-time console streaming, and explicit control semantics designed for headless environments and power users.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

### 🎯 Core Capabilities

- **Interactive REPL** - SSH-friendly command-line interface with history and auto-suggestions
- **Smart Tab Completion** - Context-aware completion for commands, components, files, and parameters
- **Real-time Console Viewer** - View historical and live Klipper console output with WebSocket streaming
- **File Management** - Upload, download, and manage G-code files with shell-style flags
- **Print Monitoring** - Track print progress, timing, and filament usage in real-time
- **Component Control** - Manage fans, heaters, LEDs, pins, and macros with explicit commands
- **Safe by Default** - Explicit write commands with warnings for hardware control

### 💡 Interactive Console Viewer

- **Historical Messages** - Display last 100 console messages from Klipper's gcode_store
- **Live Streaming** - Real-time WebSocket connection for instant console updates
- **Command Execution** - Send G-code commands directly from console mode
- **Tab Completion** - Auto-complete G-code command names while typing
- **Color-Coded Output** - Visual distinction between commands, errors, warnings, and responses
- **Timestamps** - See exactly when each message was received

### 📁 Advanced File Operations

- **Local Navigation** - `pwd`, `ls`, `cd` commands for your local filesystem
- **Remote Management** - Create directories, list files with advanced filtering
- **Upload/Download** - Transfer files between local system and printer
- **Shell-Style Flags** - `-t` (time), `-S` (size), `-r` (reverse), `-a` (all/hidden)
- **Wildcard Patterns** - Filter files with `*.gcode`, `test_*`, etc.
- **Smart Quoting** - Automatic quote handling for filenames with spaces

### 🔧 Component Control

- **Read Operations** - `get_sensor`, `get_fan`, `get_heater`, `get_led`, `get_pin`
- **Write Operations** - `set_fan`, `set_led`, `set_heater`, `set_pin` with explicit parameters
- **Macro Execution** - Run macros with parameter-aware completion
- **Motion Control** - `home`, `extrude` commands with safety checks

---

## Prerequisites

- **Python 3.10+** - Required for modern type hints and async support
- **Klipper** - Running on your 3D printer
- **Moonraker** - API server for Klipper (http://localhost:7125 by default)
- **Network Access** - SSH access to your printer (for remote use)

### Tested Environments

- Raspberry Pi 4 with MainsailOS
- Raspberry Pi 3B+ with FluiddPi
- Linux x86_64 systems
- macOS (Intel and Apple Silicon)

---

## Installation

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console

# Create virtual environment
python3 -m venv venv

# Install dependencies
./venv/bin/pip install -e .
```

### Method 2: Direct Installation

```bash
# Install directly from GitHub
pip install git+https://github.com/darkoperator/Klipper-Console.git
```

### Method 3: Development Installation

```bash
# Clone and install in editable mode for development
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Method 4: Moonraker Update Manager (Recommended for Klipper Users)

Enable automatic updates through Mainsail/Fluidd web interface alongside Klipper and Moonraker.

#### Step 1: Install Klipper-Console

SSH into your printer and run:

```bash
cd ~
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console
./scripts/install.sh
```

The installer will create a virtual environment and install all dependencies automatically.

#### Step 2: Configure Moonraker

Add this to your `~/printer_data/config/moonraker.conf` file:

```ini
[update_manager klipper-console]
type: git_repo
path: ~/Klipper-Console
origin: https://github.com/darkoperator/Klipper-Console.git
primary_branch: main
virtualenv: ~/klipper-console-env
requirements: pyproject.toml
install_script: scripts/install.sh
channel: stable
```

#### Step 3: Restart Moonraker

```bash
sudo systemctl restart moonraker
```

Now Klipper-Console will appear in your update manager and can be updated with one click!

#### Step 4: Run Klipper-Console

```bash
~/klipper-console-env/bin/klipper-console
```

Or create an alias in your `~/.bashrc`:
```bash
alias klipper-console='~/klipper-console-env/bin/klipper-console'
```

For detailed installation instructions and troubleshooting, see [docs/user-guide/INSTALLATION.md](docs/user-guide/INSTALLATION.md).

---

## Quick Start

### Local Printer (Default)

If Moonraker is running on the same machine at the default port:

```bash
./klipper-console.sh
```

This connects to `http://localhost:7125` with no authentication.

### Remote Printer

Connect to a remote printer with custom URL:

```bash
./klipper-console.sh --url http://192.168.1.100:7125
```

### With Authentication

If your Moonraker instance requires authentication:

```bash
./klipper-console.sh --url http://192.168.1.100:7125 --api-key YOUR_API_KEY
```

### Custom Timeout

For printers with slow homing or long operations:

```bash
./klipper-console.sh --timeout 180  # 3 minutes
```

---

## Usage

### Basic Commands

```bash
# Get help
klipper> help
klipper> help get_sensor

# Check printer status
klipper> get_status
klipper> get_print_status

# Monitor components
klipper> get_sensor              # Show all temperature sensors
klipper> get_sensor chamber      # Show specific sensor
klipper> get_fan                 # Show all fans
klipper> get_fan BedFans         # Show specific fan
```

### Interactive Console Viewer

Watch real-time console output and send commands:

```bash
klipper> console
[Loading historical console messages...]
[Connected to real-time console output]

[12:34:56] // Recv: ok
[12:34:57] M117 Test message
[12:34:57] // Recv: ok

█ > G28                          # Send commands with tab completion
[12:35:10] // Recv: ok

Press Ctrl+C to exit
```

### File Management

```bash
# List files with sorting
klipper> get_file                # List all G-code files
klipper> get_file -t             # Sort by time (newest first)
klipper> get_file -S *.gcode     # Sort by size, filter by pattern
klipper> get_file -t -r test_*   # Oldest first, pattern filter

# Local filesystem navigation
klipper> pwd                     # Show current local directory
klipper> ls -t                   # List local files by time
klipper> cd ~/gcode              # Change to local directory

# Upload and download
klipper> upload_file test.gcode                              # Upload from current directory
klipper> upload_file /tmp/part.gcode gcodes/subfolder       # Upload to subfolder
klipper> download_file "my file.gcode" ./downloads/         # Download (auto-quoted)

# Directory management
klipper> mkdir test_prints       # Create directory on printer
klipper> list_dir -S             # List directories by size
```

### Component Control

```bash
# Control fans
klipper> set_fan BedFans SPEED=0.5    # Set to 50%
klipper> set_fan BedFans SPEED=0      # Turn off

# Control heaters (⚠️ Physical hardware control)
klipper> set_heater extruder TEMP=200
klipper> set_heater bed TEMP=60

# Control LEDs
klipper> set_led chamber_light RED=1.0 GREEN=1.0 BLUE=1.0

# Run macros
klipper> run BED_MESH_CALIBRATE
klipper> run PRINT_START EXTRUDER=210 BED=60
```

### Motion Control

```bash
# Home axes
klipper> home           # Home all axes
klipper> home X Y       # Home specific axes

# Extrude/retract
klipper> extrude AMOUNT=10 FEEDRATE=300    # Extrude 10mm
klipper> extrude AMOUNT=-5 FEEDRATE=300    # Retract 5mm
```

---

## Configuration

### Command-Line Options

```bash
./klipper-console.sh [OPTIONS]

Options:
  --url URL              Moonraker URL (default: http://localhost:7125)
  --api-key KEY          API key for authentication
  --timeout SECONDS      Request timeout (default: 120)
  -h, --help            Show help message
```

### Environment Variables

You can also configure via environment variables:

```bash
export MOONRAKER_URL="http://192.168.1.100:7125"
export MOONRAKER_API_KEY="your-api-key"
export MOONRAKER_TIMEOUT="180"

./klipper-console.sh
```

### Configuration File (Future)

Configuration file support is planned for v1.0. See [PRD.md](docs/architecture/PRD.md) for details.

---

## Available Commands

### Component Inspection
- `get_sensor [name]` - Temperature sensors
- `get_fan [name]` - Fans
- `get_led [name]` - LEDs and neopixels
- `get_heater [name]` - Heaters
- `get_pin [name]` - Output pins
- `get_toolhead` - Toolhead status and homing state
- `get_endstops` - Endstop status
- `get_status` - Overall printer status
- `get_print_status` - Current print job with progress
- `get_macro [name]` - Macro information
- `get_gcode [command]` - G-code command help

### Component Control
- `set_fan <name> SPEED=<0.0-1.0>` - Set fan speed
- `set_led <name> RED=<0-1> GREEN=<0-1> BLUE=<0-1>` - Set LED color
- `set_heater <name> TEMP=<celsius>` - Set heater temperature ⚠️
- `set_pin <name> VALUE=<0.0-1.0>` - Set output pin value
- `run <macro> [PARAM=value ...]` - Execute macro
- `run_gcode <command>` - Execute G-code command
- `home [X] [Y] [Z]` - Home axes
- `extrude AMOUNT=<mm> [FEEDRATE=<mm/min>]` - Extrude/retract filament

### File Operations (Local)
- `pwd` - Show current local directory
- `ls [flags] [pattern]` - List local files
- `cd <path>` - Change local directory

### File Operations (Remote)
- `get_file [flags] [pattern]` - List printer files with sorting/filtering
- `mkdir <path>` - Create directory on printer
- `list_dir [flags] [pattern]` - List printer directories
- `upload_file <local> [remote]` - Upload file to printer
- `download_file <remote> <local>` - Download file from printer
- `delete_file <filename>` - Delete file
- `move_file <source> <dest>` - Move/rename file
- `copy_file <source> <dest>` - Copy file
- `print_file <filename>` - Start printing file

### Console & Debugging
- `console` - Enter interactive console viewer with real-time output

### Utility
- `help [command]` - Show help information
- `exit` / `quit` - Exit console

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black klipper_console/
```

### Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/darkoperator/Klipper-Console/issues) on GitHub.

---

## Troubleshooting

### Connection Issues

**Problem**: `Failed to connect to Moonraker`

**Solutions**:
- Verify Moonraker is running: `systemctl status moonraker`
- Check the URL is correct: `curl http://localhost:7125/server/info`
- Verify network connectivity if using remote URL
- Check firewall settings

### Timeout Errors

**Problem**: Commands timeout on operations like homing

**Solution**: Increase timeout with `--timeout` flag:
```bash
./klipper-console.sh --timeout 180
```

### Authentication Errors

**Problem**: `401 Unauthorized` or authentication failures

**Solutions**:
- Verify API key is correct
- Check Moonraker authentication settings in `moonraker.conf`
- Ensure API key has proper permissions

### Permission Errors

**Problem**: Cannot read/write files

**Solutions**:
- Check file permissions on printer
- Verify you have write access to local directories
- Run with appropriate user permissions

### WebSocket Connection Fails

**Problem**: Console viewer shows "WebSocket connection failed"

**Solutions**:
- Verify Moonraker WebSocket port (usually 7125)
- Check firewall allows WebSocket connections
- Console viewer will still show historical messages

---

## Architecture

Klipper Console is built with a modular architecture:

- **Shell** - Interactive REPL with prompt_toolkit
- **Parser** - Command parsing with shlex
- **Registry** - Command registration and routing
- **Handlers** - Business logic for commands
- **Moonraker Client** - HTTP client for Moonraker API
- **WebSocket Client** - Real-time streaming (console viewer)
- **Render** - Rich-based output formatting
- **Completion** - Context-aware tab completion
- **Models** - Data models for printer components

See [PRD.md](docs/architecture/PRD.md) for detailed architecture and design decisions.

---

## Roadmap

### Current Status: Phase 5 (Stability & Optimization) ✓

- ✅ Phase 0 - Foundation
- ✅ Phase 1 - Interactive MVP
- ✅ Phase 2 - Control & Discoverability
- ✅ Phase 3 - File Management
- ✅ Phase 4 - Console Viewer
- ✅ Phase 5 - Stability & Optimization

### Planned: v1.0

- Configuration file support
- Plugin/extension system
- Script mode with deterministic output
- Comprehensive documentation
- User guide and tutorials

See [PRD.md](docs/architecture/PRD.md) for complete roadmap.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Klipper** - The amazing 3D printer firmware by Kevin O'Connor
- **Moonraker** - The API server by Arksine
- **prompt_toolkit** - Interactive command-line interfaces
- **Rich** - Beautiful terminal formatting
- **httpx** - Modern HTTP client

---

## Links

- **GitHub Repository**: https://github.com/darkoperator/Klipper-Console
- **Issue Tracker**: https://github.com/darkoperator/Klipper-Console/issues
- **Klipper Documentation**: https://www.klipper3d.org/
- **Moonraker Documentation**: https://moonraker.readthedocs.io/

---

**Made with ❤️ for the Klipper community**
