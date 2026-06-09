#!/usr/bin/env bash
# Quick interactive demo of ece4-exp commands
# Shows the main workflow and commands

# Note: Don't use set -e because some commands show expected errors
set +e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       ece4-exp: EC-Earth4 Made Easy - Quick Demo        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Step 1: List available recipes
echo -e "${CYAN}📋 Step 1: What recipes are available?${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp list"
echo ""
./ece4-exp list
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 2: Show info command (may show errors if not configured)
echo -e "${CYAN}⚙️  Step 2: Check current configuration${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp info"
echo ""
echo -e "${YELLOW}Note: This shows your current defaults from ~/.config/ece4-exp/defaults.yml${NC}"
echo -e "${YELLOW}      If not configured yet, you'll see what's missing${NC}"
echo ""
./ece4-exp info 2>&1 || echo -e "${YELLOW}(No user config yet - that's OK! The generate command will use provided flags)${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 3: Generate GCM experiment
echo -e "${CYAN}🚀 Step 3: Generate a GCM experiment (10 nodes, 1120 cores)${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid demo-gcm -o demo-gcm.yml"
echo ""
if ./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid demo-gcm -o demo-gcm.yml; then
    echo -e "${GREEN}✓ Created demo-gcm.yml${NC}"
else
    echo -e "${YELLOW}✗ Generation failed - check error above${NC}"
    exit 1
fi
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 4: Inspect generated file
echo -e "${CYAN}🔍 Step 4: What's in the generated file?${NC}"
echo "----------------------------------------"
echo "File size and basics:"
ls -lh demo-gcm.yml
echo ""
echo "Components configured:"
grep "components:" demo-gcm.yml
echo ""
echo "Model grids:"
grep "grid:" demo-gcm.yml | head -2
echo ""
echo "Job configuration (nodes):"
grep -A 1 "groups:" demo-gcm.yml | head -3
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 5: Validate
echo -e "${CYAN}✅ Step 5: Validate the configuration${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp validate demo-gcm.yml"
echo ""
./ece4-exp validate demo-gcm.yml
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 6: Try with dry-run
echo -e "${CYAN}👀 Step 6: Preview without writing (--dry-run)${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp generate --recipe amip-sr.yml --sim-procs 896 --expid demo-amip --dry-run"
echo ""
echo "First 30 lines of output:"
./ece4-exp generate --recipe amip-sr.yml --sim-procs 896 --expid demo-amip --dry-run 2>/dev/null | head -30
echo ""
echo "... (output truncated)"
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 7: Ocean-only experiment
echo -e "${CYAN}🌊 Step 7: Generate ocean-only experiment (2 nodes, 224 cores)${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid demo-omip -o demo-omip.yml"
echo ""
if ./ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid demo-omip -o demo-omip.yml 2>&1 | tail -8; then
    echo ""
    echo "Components (note: no OIFS - ocean only!):"
    grep "components:" demo-omip.yml
    echo ""
    echo -e "${GREEN}✓ Created demo-omip.yml${NC}"
else
    echo -e "${YELLOW}✗ Generation failed${NC}"
fi
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 8: Compare file sizes
echo -e "${CYAN}📊 Step 8: Compare configurations${NC}"
echo "----------------------------------------"
echo "Generated experiment files:"
ls -lh demo-*.yml 2>/dev/null || echo "No demo files found"
echo ""
echo "Line counts:"
wc -l demo-*.yml 2>/dev/null || echo "No demo files found"
echo ""
echo "Notice: All experiment configs are compact (~230 lines)"
echo "        Platform/build configs are NOT included (loaded separately by workflow)"
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 9: Show help
echo -e "${CYAN}❓ Step 9: Get help on any command${NC}"
echo "----------------------------------------"
echo "$ ./ece4-exp --help"
echo ""
./ece4-exp --help | head -25
echo "..."
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                      Demo Complete!                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}⏱️  Time to configure: ~1 minute${NC}"
echo -e "${GREEN}📁 Files created: demo-gcm.yml, demo-omip.yml${NC}"
echo -e "${GREEN}🎯 Both are ready-to-use EC-Earth4 configurations${NC}"
echo ""
echo "Commands demonstrated:"
echo "  ✓ list      - See available recipes"
echo "  ✓ info      - Check current configuration"
echo "  ✓ generate  - Create experiment configs"
echo "  ✓ validate  - Verify configurations"
echo "  ✓ --dry-run - Preview without writing"
echo ""
echo "Next steps:"
echo "  1. Run: ./ece4-exp init-user"
echo "     (Creates ~/.config/ece4-exp/defaults.yml with your settings)"
echo ""
echo "  2. Set your defaults:"
echo "     - platform, account, scratch path, etc."
echo "     - Then you only need: ./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120"
echo ""
echo "  3. Read full documentation:"
echo "     - DEMO.md for detailed walkthrough"
echo "     - README.md for complete guide"
echo "     - docs/presentation/ece4-exp-intro.{html,pdf} for slides"
echo ""
echo -e "${YELLOW}Clean up demo files:${NC}"
echo "  rm demo-*.yml ece4_exp/demo-*_pristine.yml"
echo ""
