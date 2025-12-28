# Klipper-Console Installation Guide

This guide covers all installation methods for Klipper-Console, from simple automatic installation to manual development setups.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Recommended: Moonraker Update Manager](#recommended-moonraker-update-manager)
- [Manual Installation](#manual-installation)
- [Development Installation](#development-installation)
- [Uninstallation](#uninstallation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **python3-venv** (Virtual environment support)

### Recommended for Moonraker Integration

- **Klipper** (3D printer firmware)
- **Moonraker** (Klipper API server)
- **Mainsail** or **Fluidd** (Web interface)

### Checking Prerequisites

```bash
# Check Python version (must be 3.10+)
python3 --version

# Check if pip is installed
python3 -m pip --version

# Check if venv is available
python3 -m venv --help
```

If you're missing `python3-venv` on Debian/Ubuntu:
```bash
sudo apt install python3-venv
```

---

## Recommended: Moonraker Update Manager

This method enables automatic updates through your Mainsail or Fluidd web interface, alongside Klipper and Moonraker.

### Step 1: Install Klipper-Console

SSH into your printer and run:

```bash
cd ~
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console
./scripts/install.sh
```

The installer will:
- Check Python version and dependencies
- Create a virtual environment at `~/klipper-console-env`
- Install Klipper-Console and all dependencies
- Display next steps

### Step 2: Configure Moonraker

Add this section to your `~/printer_data/config/moonraker.conf` file:

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

### Step 3: Restart Moonraker

```bash
sudo systemctl restart moonraker
```

### Step 4: Verify Installation

1. Open your Mainsail or Fluidd web interface
2. Navigate to the Update Manager section
3. You should see "klipper-console" listed alongside Klipper and Moonraker
4. The current version should be displayed

### Step 5: Run Klipper-Console

```bash
~/klipper-console-env/bin/klipper-console
```

Or create an alias for convenience (add to `~/.bashrc`):

```bash
alias klipper-console='~/klipper-console-env/bin/klipper-console'
```

Then run:
```bash
source ~/.bashrc
klipper-console
```

---

## Manual Installation

For users who want to install without Moonraker integration, or on non-Klipper systems.

### Method 1: Install from GitHub (Recommended for Manual Install)

```bash
python3 -m venv ~/klipper-console-env
source ~/klipper-console-env/bin/activate
pip install git+https://github.com/darkoperator/Klipper-Console.git
```

Run the console:
```bash
~/klipper-console-env/bin/klipper-console
```

### Method 2: Clone and Install Locally

```bash
cd ~
git clone https://github.com/darkoperator/Klipper-Console.git
cd Klipper-Console
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Run the console:
```bash
./venv/bin/klipper-console
```

Or use the wrapper script:
```bash
./klipper-console.sh
```

---

## Development Installation

For contributors and developers who want to modify the code.

### Step 1: Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/Klipper-Console.git
cd Klipper-Console
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install in Editable Mode with Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- Klipper-Console in editable mode
- Development tools (pytest, black, ruff, mypy)
- Code coverage tools

### Step 4: Verify Installation

```bash
# Run tests
pytest

# Check code style
black --check klipper_console/
ruff check klipper_console/

# Run type checking
mypy klipper_console/
```

### Step 5: Run the Console

```bash
./klipper-console.sh
```

Or directly:
```bash
./venv/bin/klipper-console
```

---

## Uninstallation

### Remove Moonraker Integration

1. Remove the `[update_manager klipper-console]` section from `~/printer_data/config/moonraker.conf`
2. Restart Moonraker:
   ```bash
   sudo systemctl restart moonraker
   ```

### Remove Installation Files

```bash
# Remove virtual environment
rm -rf ~/klipper-console-env

# Remove source code
rm -rf ~/Klipper-Console

# Remove alias (if added to ~/.bashrc)
# Edit ~/.bashrc and remove the alias line
```

---

## Troubleshooting

### Python Version Too Old

**Error:** `Python 3.X found, but Python 3.10 or higher is required`

**Solution:** Install Python 3.10 or higher. On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

Then specify the Python version during installation:
```bash
python3.11 -m venv ~/klipper-console-env
```

### Virtual Environment Creation Fails

**Error:** `The virtual environment was not created successfully`

**Solution:** Install the venv module:

```bash
# Debian/Ubuntu
sudo apt install python3-venv

# Raspberry Pi OS
sudo apt install python3-full python3-venv
```

### Permission Denied Errors

**Error:** `Permission denied` when running install script

**Solutions:**

1. Make script executable:
   ```bash
   chmod +x scripts/install.sh
   ```

2. Run with bash directly:
   ```bash
   bash scripts/install.sh
   ```

3. Don't use sudo - the script should run as your normal user

### Moonraker Not Detecting Updates

**Problem:** Klipper-Console doesn't appear in update manager

**Solutions:**

1. **Check configuration syntax** in moonraker.conf:
   - Ensure proper indentation (no tabs)
   - Verify all fields are present
   - Check path points to actual installation directory

2. **Verify installation path matches config:**
   ```bash
   ls -la ~/Klipper-Console
   ls -la ~/klipper-console-env
   ```

3. **Check Moonraker logs:**
   ```bash
   tail -f ~/printer_data/logs/moonraker.log
   ```

4. **Verify git repository:**
   ```bash
   cd ~/Klipper-Console
   git status
   git remote -v
   ```

5. **Restart Moonraker after config changes:**
   ```bash
   sudo systemctl restart moonraker
   ```

### Update Fails in Web Interface

**Problem:** Update starts but fails during execution

**Solutions:**

1. **Check Moonraker has write permissions:**
   ```bash
   ls -la ~/Klipper-Console
   # Should be owned by your user (e.g., pi)
   ```

2. **Check git repository status:**
   ```bash
   cd ~/Klipper-Console
   git status
   # Should show "nothing to commit, working tree clean"
   ```

3. **Manually test install script:**
   ```bash
   cd ~/Klipper-Console
   ./scripts/install.sh
   ```

4. **Check virtual environment Python version:**
   ```bash
   ~/klipper-console-env/bin/python --version
   # Should be 3.10 or higher
   ```

### Console Won't Start

**Problem:** `klipper-console` command not found or fails to start

**Solutions:**

1. **Check virtual environment exists:**
   ```bash
   ls -la ~/klipper-console-env/bin/klipper-console
   ```

2. **Activate virtual environment and test:**
   ```bash
   source ~/klipper-console-env/bin/activate
   which klipper-console
   klipper-console --help
   ```

3. **Check for import errors:**
   ```bash
   ~/klipper-console-env/bin/python -c "import klipper_console"
   ```

4. **Reinstall dependencies:**
   ```bash
   cd ~/Klipper-Console
   ./scripts/install.sh
   ```

### Connection Issues

**Problem:** Can't connect to Moonraker

**Solutions:**

See the [USAGE.md](USAGE.md) guide for connection troubleshooting.

### Getting Help

If you encounter issues not covered here:

1. **Check existing issues:** https://github.com/darkoperator/Klipper-Console/issues
2. **Review documentation:** See [README.md](../../README.md) and [USAGE.md](USAGE.md)
3. **Open a new issue:** Include:
   - Python version (`python3 --version`)
   - Operating system
   - Installation method used
   - Complete error message
   - Relevant log files

---

## Next Steps

After installation, see the [USAGE.md](USAGE.md) guide for:
- Connecting to your printer
- Available commands
- Tab completion features
- Configuration options
