#!/usr/bin/env bash
#
# setup.sh - Simple setup script for ece4-exp development
#
# For users: Just run `pip install ece4-exp` instead!
# This script is only needed for development from source.
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }

echo "========================================="
echo "  ece4-exp Development Setup"
echo "========================================="
echo ""

# Check if running from source
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Run this script from the ece4-exp repository root"
    exit 1
fi

# Inform about simpler installation
echo -e "${CYAN}Note:${NC} For regular users, just run: pip install ece4-exp"
echo "This setup script is for development from source."
echo ""

# Install in editable mode
log_info "Installing ece4-exp in editable mode..."
if pip install -e . ; then
    log_info "Installation successful"
else
    echo "Error: Installation failed"
    exit 1
fi

# Test installation
log_info "Testing installation..."
if ece4-exp --help > /dev/null 2>&1; then
    log_info "ece4-exp is working correctly!"
else
    log_warn "Installation succeeded but command not in PATH"
    echo "Try: source ~/.bashrc or restart your shell"
fi

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""

# Optional: Offer to run init-user
if [[ -t 0 ]]; then  # Check if interactive
    read -p "Configure user defaults now? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ece4-exp init-user
    else
        log_info "Skipped. Run 'ece4-exp init-user' later to configure defaults."
    fi
fi

echo ""
echo "Next steps:"
echo "  1. List recipes:       ${CYAN}ece4-exp list${NC}"
echo "  2. Try the demo:       ${CYAN}./QUICK_DEMO.sh${NC}"
echo "  3. Generate config:    ${CYAN}ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --dry-run${NC}"
echo ""
log_info "Happy experimenting!"
