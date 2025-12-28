#!/bin/bash
# Klipper-Console Installation Script
# This script installs Klipper-Console for use with Moonraker update_manager

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KLIPPER_CONSOLE_DIR="$(dirname "$SCRIPT_DIR")"
KLIPPER_CONSOLE_ENV="${HOME}/klipper-console-env"
PYTHON_MIN_VERSION="3.10"
PYTHON_BIN="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}$1${NC}"
}

# Check Python version
check_python_version() {
    print_info "Checking Python version..."

    if ! command -v $PYTHON_BIN &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.10 or higher."
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python $PYTHON_VERSION found, but Python $PYTHON_MIN_VERSION or higher is required."
        print_info "Please install Python $PYTHON_MIN_VERSION or higher and try again."
        exit 1
    fi

    print_success "Python $PYTHON_VERSION found (meets requirement: >=$PYTHON_MIN_VERSION)"
}

# Check if pip and venv are available
check_requirements() {
    print_info "Checking for required Python packages..."

    if ! $PYTHON_BIN -m pip --version &> /dev/null; then
        print_error "pip is not installed. Please install pip for Python 3."
        exit 1
    fi

    if ! $PYTHON_BIN -m venv --help &> /dev/null; then
        print_error "venv module is not available. Please install python3-venv package."
        print_info "On Debian/Ubuntu: sudo apt install python3-venv"
        exit 1
    fi

    print_success "All requirements met"
}

# Create or update virtual environment
create_virtualenv() {
    print_info "Setting up virtual environment at $KLIPPER_CONSOLE_ENV..."

    if [ -d "$KLIPPER_CONSOLE_ENV" ]; then
        print_info "Virtual environment already exists, checking Python version..."

        # Check if existing venv has correct Python version
        VENV_PYTHON="$KLIPPER_CONSOLE_ENV/bin/python"
        if [ -f "$VENV_PYTHON" ]; then
            VENV_VERSION=$($VENV_PYTHON --version 2>&1 | awk '{print $2}')
            VENV_MAJOR=$(echo $VENV_VERSION | cut -d. -f1)
            VENV_MINOR=$(echo $VENV_VERSION | cut -d. -f2)

            if [ "$VENV_MAJOR" -lt 3 ] || ([ "$VENV_MAJOR" -eq 3 ] && [ "$VENV_MINOR" -lt 10 ]); then
                print_info "Existing venv has Python $VENV_VERSION, recreating with Python $PYTHON_VERSION..."
                rm -rf "$KLIPPER_CONSOLE_ENV"
                $PYTHON_BIN -m venv "$KLIPPER_CONSOLE_ENV"
            else
                print_success "Existing venv has compatible Python $VENV_VERSION"
            fi
        else
            print_info "Existing venv appears corrupted, recreating..."
            rm -rf "$KLIPPER_CONSOLE_ENV"
            $PYTHON_BIN -m venv "$KLIPPER_CONSOLE_ENV"
        fi
    else
        $PYTHON_BIN -m venv "$KLIPPER_CONSOLE_ENV"
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing Klipper-Console and dependencies..."

    cd "$KLIPPER_CONSOLE_DIR"

    # Upgrade pip first
    "$KLIPPER_CONSOLE_ENV/bin/pip" install --upgrade pip &> /dev/null

    # Install package in editable mode
    "$KLIPPER_CONSOLE_ENV/bin/pip" install -e . &> /dev/null

    if [ $? -eq 0 ]; then
        print_success "Installation complete"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Print completion message
print_completion() {
    echo ""
    print_success "========================================="
    print_success "Klipper-Console installation complete!"
    print_success "========================================="
    echo ""
    echo "Installation details:"
    echo "  - Klipper-Console directory: $KLIPPER_CONSOLE_DIR"
    echo "  - Virtual environment: $KLIPPER_CONSOLE_ENV"
    echo "  - Executable: $KLIPPER_CONSOLE_ENV/bin/klipper-console"
    echo ""
    echo "To run Klipper-Console:"
    echo "  $KLIPPER_CONSOLE_ENV/bin/klipper-console"
    echo ""
    echo "Or create an alias in your ~/.bashrc:"
    echo "  alias klipper-console='$KLIPPER_CONSOLE_ENV/bin/klipper-console'"
    echo ""
    print_info "========================================="
    print_info "Moonraker Update Manager Setup"
    print_info "========================================="
    echo ""
    echo "To enable automatic updates through Mainsail/Fluidd, add this to"
    echo "your ~/printer_data/config/moonraker.conf file:"
    echo ""
    echo "[update_manager klipper-console]"
    echo "type: git_repo"
    echo "path: $KLIPPER_CONSOLE_DIR"
    echo "origin: https://github.com/darkoperator/Klipper-Console.git"
    echo "primary_branch: main"
    echo "virtualenv: $KLIPPER_CONSOLE_ENV"
    echo "requirements: pyproject.toml"
    echo "install_script: scripts/install.sh"
    echo "channel: stable"
    echo ""
    echo "After adding the configuration, restart Moonraker:"
    echo "  sudo systemctl restart moonraker"
    echo ""
}

# Main installation flow
main() {
    echo ""
    print_info "========================================="
    print_info "Klipper-Console Installation Script"
    print_info "========================================="
    echo ""

    check_python_version
    check_requirements
    create_virtualenv
    install_dependencies
    print_completion
}

# Run main function
main
