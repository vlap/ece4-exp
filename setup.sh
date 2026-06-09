#!/usr/bin/env bash
#
# setup.sh - Quick setup script for ece4-exp
#
# Usage: ./setup.sh [--interactive]
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_prompt() { echo -e "${CYAN}?${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }

echo "========================================="
echo "  ece4-exp Setup"
echo "========================================="
echo ""

# 1. Check Python
log_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log_info "Found Python $PYTHON_VERSION"

# 2. Install requirements
log_info "Installing Python dependencies..."
if pip3 install -q -r requirements.txt; then
    log_info "Dependencies installed successfully"
else
    log_warn "Failed to install some dependencies. You may need to install manually."
fi

# 3. Initialize user config
echo ""
log_info "Setting up user configuration..."

INTERACTIVE="false"
if [[ "${1:-}" == "--interactive" ]]; then
    INTERACTIVE="true"
fi

if [[ "$INTERACTIVE" == "true" ]]; then
    # Interactive setup
    log_prompt "Let's configure your defaults..."
    echo ""

    # Platform
    log_prompt "Which HPC platform do you use?"
    echo "  1) bsc-marenostrum5 (BSC)"
    echo "  2) ecmwf-hpc2020 (ECMWF)"
    echo "  3) csc-mahti (CSC Finland)"
    echo "  4) other (manual setup)"
    read -p "Choice [1]: " platform_choice
    platform_choice=${platform_choice:-1}

    case $platform_choice in
        1) platform="bsc-marenostrum5" ;;
        2) platform="ecmwf-hpc2020" ;;
        3) platform="csc-mahti" ;;
        *) platform="bsc-marenostrum5" ;;
    esac

    # Account
    read -p "Your HPC account/project: " account
    account=${account:-"your-project"}

    # Scratch
    read -p "Your scratch directory (e.g., /gpfs/scratch/username): " scratch
    scratch=${scratch:-"/gpfs/scratch/username"}

    # Create config
    ./ece4-exp init-user

    # Update with user values
    config_file="$HOME/.config/ece4-exp/defaults.yml"
    sed -i "s|account: bsc32|account: $account|g" "$config_file"
    sed -i "s|/gpfs/scratch/username|$scratch|g" "$config_file"
    sed -i "s|platform: bsc-marenostrum5|platform: $platform|g" "$config_file"

    log_info "Configuration saved to $config_file"
else
    # Non-interactive setup
    ./ece4-exp init-user
    log_info "Created ~/.config/ece4-exp/defaults.yml"
    log_warn "Edit this file to set your platform, account, and scratch directory"
fi

# 4. Install bash completion (optional)
echo ""
if command -v bash &> /dev/null && [[ -t 0 ]]; then
    log_prompt "Install bash completion and add to ~/.bashrc? [Y/n]"
    read -p "" install_completion
    install_completion=${install_completion:-Y}

    if [[ "$install_completion" =~ ^[Yy]$ ]]; then
        completion_dest="$HOME/.local/share/bash-completion/completions"
        mkdir -p "$completion_dest"
        cp scripts/ece4-exp-completion.sh "$completion_dest/ece4-exp"
        log_info "Bash completion installed to $completion_dest/ece4-exp"

        # Add to ~/.bashrc if not already there
        bashrc="$HOME/.bashrc"
        completion_source="source $completion_dest/ece4-exp"

        if [ -f "$bashrc" ]; then
            if ! grep -qF "$completion_source" "$bashrc"; then
                echo "" >> "$bashrc"
                echo "# ece4-exp bash completion" >> "$bashrc"
                echo "$completion_source" >> "$bashrc"
                log_info "Added completion source to ~/.bashrc"
                log_warn "Restart your shell or run: source ~/.bashrc"
            else
                log_info "Completion already sourced in ~/.bashrc"
            fi
        else
            log_warn "~/.bashrc not found. To enable completion, add to your shell config:"
            echo "  $completion_source"
        fi
    fi
elif command -v bash &> /dev/null; then
    # Non-interactive
    log_info "Skipping bash completion (non-interactive mode)"
    log_info "To install later: cp scripts/ece4-exp-completion.sh ~/.local/share/bash-completion/completions/ece4-exp"
fi

# 5. Test installation
echo ""
log_info "Testing installation..."
if ./ece4-exp list > /dev/null 2>&1; then
    log_info "ece4-exp is working correctly!"
else
    log_warn "There may be an issue. Try running: ./ece4-exp --help"
fi

# 6. Next steps
echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit your config:"
echo "     ${CYAN}nano ~/.config/ece4-exp/defaults.yml${NC}"
echo ""
echo "  2. List available recipes:"
echo "     ${CYAN}./ece4-exp list${NC}"
echo ""
echo "  3. Generate your first experiment:"
echo "     ${CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test001 --dry-run${NC}"
echo ""
echo "  4. Read the documentation:"
echo "     ${CYAN}cat README.md${NC}"
echo ""
log_info "Happy experimenting!"
