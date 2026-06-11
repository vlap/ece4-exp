#!/usr/bin/env python3
"""
init_config.py

Interactive setup to create user configuration directory and defaults file.
"""

import sys
from pathlib import Path
from . import paths
from .yaml_util import log_info, log_warn, log_error, COLOR_CYAN, COLOR_GREEN, COLOR_NC


def init_user_config():
    """Interactive setup to create ~/.config/ece4-exp/defaults.yml.

    Asks user for platform, account, and username to create a working configuration.
    """
    config_dir = paths.USER_CONFIG_DIR
    defaults_file = paths.USER_DEFAULTS_FILE

    print()
    print("=" * 70)
    print(" ece4-exp Interactive Setup")
    print("=" * 70)
    print()

    # Create directories if they don't exist
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Created directory: {config_dir}")

    # Create subdirectories
    for subdir in [paths.USER_RECIPES_DIR, paths.USER_PLATFORMS_DIR]:
        if not subdir.exists():
            subdir.mkdir(parents=True, exist_ok=True)

    # Check if config already exists
    if defaults_file.exists():
        print()
        log_warn(f"Configuration file already exists: {defaults_file}")
        print()
        print("Options:")
        print(f"  • View current config: {COLOR_CYAN}cat {defaults_file}{COLOR_NC}")
        print(f"  • Edit config: {COLOR_CYAN}nano {defaults_file}{COLOR_NC}")
        print(f"  • Reset config: {COLOR_CYAN}rm {defaults_file} && ece4-exp setup{COLOR_NC}")
        print()
        return

    # Interactive questions
    print("Answer a few questions to create your configuration:")
    print()

    # Question 1: Platform
    print(f"{COLOR_CYAN}1. Which HPC platform do you use?{COLOR_NC}")
    print("   [1] BSC MareNostrum 5")
    print("   [2] ECMWF HPC2020")
    print()
    while True:
        platform_choice = input("Enter 1 or 2: ").strip()
        if platform_choice in ["1", "2"]:
            break
        print("Please enter 1 or 2")

    if platform_choice == "1":
        platform = "bsc-marenostrum5"
        qos_default = "gp_bsces"
        account_default = "bsc32"
        user_example = "bsc32XXX"
    else:
        platform = "ecmwf-hpc2020"
        qos_default = "normal"
        account_default = "spesiccf"
        user_example = "c3YY"

    print()

    # Question 2: Account/Project
    print(f"{COLOR_CYAN}2. What is your project/account name?{COLOR_NC}")
    print(f"   (e.g., {account_default})")
    print()
    account = input(f"Account [{account_default}]: ").strip() or account_default
    print()

    # Question 3: QoS (optional, show default)
    print(f"{COLOR_CYAN}3. QoS (Quality of Service)?{COLOR_NC}")
    print(f"   Default for {platform}: {qos_default}")
    print()
    qos = input(f"QoS [{qos_default}]: ").strip() or qos_default
    print()

    # Question 4: Username (optional, for documentation)
    print(f"{COLOR_CYAN}4. Your username (optional, for reference)?{COLOR_NC}")
    print(f"   (e.g., {user_example})")
    print()
    username = input(f"Username [skip]: ").strip()
    print()

    # Build config content from user answers
    user_comment = f"# User: {username}" if username else ""

    config_content = f"""# ece4-exp configuration (created by 'ece4-exp setup')
# Edit this file to change your defaults

# ═══════════════════════════════════════════════════════════
# Platform & EC-Earth4 Version
# ═══════════════════════════════════════════════════════════
platform: {platform}
launcher: slurm-wrapper-taskset  # Default, rarely needs changing
kind: auto                       # Auto-detects from recipe

repo_owner: ec-earth             # Official EC-Earth4 repo
repo_branch: v4.1.8              # Latest stable version

# ═══════════════════════════════════════════════════════════
# Your HPC Account
# ═══════════════════════════════════════════════════════════
account: {account}
qos: {qos}
{user_comment}

# ═══════════════════════════════════════════════════════════
# Optional: Auto-fill recipe/procs to skip typing them
# ═══════════════════════════════════════════════════════════
# recipe: gcm-sr                 # gcm-sr, omip-sr, amip-sr, ccycle-sr
# sim_procs: 1120                # 1120 (10 nodes MN5), 224 (2 nodes), etc.

# ═══════════════════════════════════════════════════════════
# Notes
# ═══════════════════════════════════════════════════════════
# Walltime: Set automatically per experiment type in platform configs
#   CPLD-SR: 1h, OMIP-SR: 30min, AMIP-SR: 30min, CCCL-SR: 1.5h
#   Override: ece4-exp generate RECIPE PROCS EXPID --walltime HOURS
#
# Resolution order: CLI args > this file > platform defaults
#
# Usage:
#   ece4-exp generate gcm-sr 1120 a001
#   ece4-exp generate omip-sr 224 o001 --walltime 2
"""

    try:
        defaults_file.write_text(config_content)
        print()
        print("=" * 70)
        log_info(f"✓ Configuration saved to: {COLOR_CYAN}{defaults_file}{COLOR_NC}")
        print("=" * 70)
        print()
        print(f"{COLOR_GREEN}You're all set!{COLOR_NC} Try generating your first experiment:")
        print()
        print(f"  {COLOR_CYAN}ece4-exp list{COLOR_NC}")
        print(f"  {COLOR_CYAN}ece4-exp generate gcm-sr 1120 a001{COLOR_NC}")
        print()
        print("Your configuration:")
        print(f"  Platform: {platform}")
        print(f"  Account:  {account}")
        print(f"  QoS:      {qos}")
        if username:
            print(f"  User:     {username}")
        print()
        print(f"To change settings: {COLOR_CYAN}nano {defaults_file}{COLOR_NC}")
        print()

    except Exception as e:
        log_error(f"Failed to create configuration: {e}")
        sys.exit(1)


def main():
    """Command-line entry point."""
    init_user_config()

if __name__ == "__main__":
    main()
