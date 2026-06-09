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
echo "========================================="
echo "  User Configuration"
echo "========================================="
echo ""
echo "ece4-exp stores your personal defaults (platform, account, etc.)"
echo "so you don't have to type them with every command."
echo ""
echo -e "These will be saved to: ${CYAN}~/.config/ece4-exp/defaults.yml${NC}"
echo ""
echo "How it works:"
echo "  • Set once: platform, account, walltime, etc."
echo "  • Generate experiments with just: --recipe <name> --sim-procs <n>"
echo "  • Override anytime with CLI flags (e.g., --platform ecmwf-hpc2020)"
echo ""

INTERACTIVE="false"
if [[ "${1:-}" == "--interactive" ]]; then
    INTERACTIVE="true"
fi

# Ask user if they want to configure now or later
if [[ "$INTERACTIVE" == "true" ]]; then
    log_prompt "Would you like to configure your defaults now? [Y/n]"
    read -p "" configure_now
    configure_now=${configure_now:-Y}

    if [[ "$configure_now" =~ ^[Nn]$ ]]; then
        log_info "Skipping configuration. You can configure later with: ./ece4-exp init-user"
    else
        # Interactive setup
        echo ""
        log_prompt "Let's configure your defaults..."
        echo ""

        # Platform
        log_prompt "Which HPC platform do you use?"
        echo "  1) bsc-marenostrum5 (BSC)"
        echo "  2) ecmwf-hpc2020 (ECMWF)"
        echo "  3) csc-mahti (CSC Finland)"
        echo "  4) Skip (configure manually later)"
        read -p "Choice [1]: " platform_choice
        platform_choice=${platform_choice:-1}

        case $platform_choice in
            1) platform="bsc-marenostrum5" ;;
            2) platform="ecmwf-hpc2020" ;;
            3) platform="csc-mahti" ;;
            4) platform="SKIP" ;;
            *) platform="bsc-marenostrum5" ;;
        esac

        if [[ "$platform" != "SKIP" ]]; then
            # Account
            echo ""
            log_prompt "Your HPC account/project (e.g., bsc32, spesimon):"
            read -p "" account
            account=${account:-"your-project"}

            # Scratch
            echo ""
            log_prompt "Your scratch directory:"
            echo "  BSC example: /gpfs/scratch/bsc32/bsc32XXX"
            echo "  ECMWF example: /scratch/ms/xx/xxxx"
            read -p "Path: " scratch
            scratch=${scratch:-"/gpfs/scratch/username"}

            # Create config
            ./ece4-exp init-user 2>&1 | grep -v "WARN"

            # Update with user values
            config_file="$HOME/.config/ece4-exp/defaults.yml"
            sed -i "s|account: bsc32|account: $account|g" "$config_file"
            sed -i "s|/gpfs/scratch/username|$scratch|g" "$config_file"
            sed -i "s|platform: bsc-marenostrum5|platform: $platform|g" "$config_file"

            echo ""
            log_info "Configuration saved to ${CYAN}$config_file${NC}"
            echo ""
            echo "Usage example:"
            echo -e "  ${CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid myexp${NC}"
            echo ""
            echo "Your platform ($platform) and account ($account) are already set!"
        else
            ./ece4-exp init-user
            config_file="$HOME/.config/ece4-exp/defaults.yml"
            echo ""
            log_warn "Configuration file created with defaults."
            log_info "Edit ${CYAN}$config_file${NC} to set your platform, account, and scratch."
        fi
    fi
else
    # Non-interactive setup
    echo "Creating default configuration file..."
    echo ""
    ./ece4-exp init-user 2>&1 | grep -v "WARN"
    config_file="$HOME/.config/ece4-exp/defaults.yml"
    echo ""
    log_info "Configuration file created: ${CYAN}$config_file${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Edit the file to set your platform, account, and scratch:"
    echo -e "     ${CYAN}nano $config_file${NC}"
    echo ""
    echo "  2. Then generate experiments with minimal commands:"
    echo -e "     ${CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120${NC}"
    echo ""
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
echo -e "     ${CYAN}nano ~/.config/ece4-exp/defaults.yml${NC}"
echo ""
echo "  2. List available recipes:"
echo -e "     ${CYAN}./ece4-exp list${NC}"
echo ""
echo "  3. Generate your first experiment:"
echo -e "     ${CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test001 --dry-run${NC}"
echo ""
echo "  4. Read the documentation:"
echo -e "     ${CYAN}cat README.md${NC}"
echo ""
log_info "Happy experimenting!"
