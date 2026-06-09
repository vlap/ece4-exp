#!/usr/bin/env python3
"""
init_config.py

Initialize user configuration directory and create example defaults file.
Simplified version - no autosubmit dependencies.
"""

import sys
from pathlib import Path
from . import paths
from .yaml_util import log_info, log_warn, log_error, COLOR_CYAN, COLOR_NC

def validate_scratch_path(scratch_path):
    """Validate scratch path and return warnings if any."""
    warnings = []

    if not scratch_path or scratch_path == "/gpfs/scratch/username":
        warnings.append("Scratch path is still the default placeholder. Update it to your actual scratch directory.")
    else:
        # Check if path exists (only warn, don't fail)
        path = Path(scratch_path)
        if not path.exists():
            warnings.append(f"Scratch path does not exist: {scratch_path}")
        elif not path.is_dir():
            warnings.append(f"Scratch path is not a directory: {scratch_path}")

    return warnings

def validate_account(account):
    """Validate account name and return warnings if any."""
    warnings = []

    if not account:
        warnings.append("Account is not set.")
    elif account in ["bsc32", "your-project"]:
        warnings.append("Account looks like a placeholder. Update it to your actual HPC account.")
    elif len(account) < 3:
        warnings.append(f"Account name seems too short: '{account}'. Verify it's correct.")

    return warnings

def init_user_config():
    """Create ~/.config/ece4-exp/ with example defaults.

    This function creates a user configuration file that stores personal defaults
    to avoid typing the same parameters repeatedly.
    """
    config_dir = paths.USER_CONFIG_DIR
    defaults_file = paths.USER_DEFAULTS_FILE

    print()
    print("=" * 70)
    print(" User Configuration Setup")
    print("=" * 70)
    print()
    print(f"Creating configuration file: {COLOR_CYAN}{defaults_file}{COLOR_NC}")
    print()
    print("This file stores your personal defaults so you can generate")
    print("experiments with minimal commands:")
    print()
    print(f"  {COLOR_CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120{COLOR_NC}")
    print()
    print("Instead of typing platform, account, etc. every time!")
    print()

    # Create directory if it doesn't exist
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Created directory: {config_dir}")

    # Create example defaults file if it doesn't exist
    if defaults_file.exists():
        print()
        log_warn(f"Configuration file already exists: {defaults_file}")
        print()
        print("Options:")
        print(f"  • View current config: {COLOR_CYAN}cat {defaults_file}{COLOR_NC}")
        print(f"  • Edit config: {COLOR_CYAN}nano {defaults_file}{COLOR_NC}")
        print(f"  • Reset config: {COLOR_CYAN}rm {defaults_file} && ./ece4-exp init-user{COLOR_NC}")
        print()
        return

    # Create example defaults with comments
    example_content = """# ece4-exp User Configuration
#
# This file stores your personal defaults for EC-Earth4 experiments.
# Set these once and never type them again!
#
# Resolution order: CLI args > this file > upstream configs

# ============================================================
# Platform Configuration (REQUIRED)
# ============================================================

# Your HPC platform - determines paths, modules, resource settings
platform: bsc-marenostrum5
# Options:
#   - bsc-marenostrum5  (BSC, Spain)
#   - ecmwf-hpc2020     (ECMWF, Italy)
#   - csc-mahti         (CSC, Finland)
#   - csc-lumi          (CSC, Finland)
#   - dkrz-levante      (DKRZ, Germany)

# Job launcher method - how to submit and run the experiment
launcher: slurm-wrapper-taskset
# Options:
#   - slurm-wrapper-taskset  (most common, uses taskset for pinning)
#   - slurm-wrapper-hostfile (alternative, uses hostfile)
#   - slurm-hetjob          (heterogeneous job, advanced)

# Launcher kind - experiment type configuration
kind: auto
# Options:
#   - auto        (auto-detect from recipe - RECOMMENDED)
#   - CPLD-SR     (coupled standard resolution)
#   - OMIP-SR     (ocean-only standard resolution)
#   - AMIP-SR     (atmosphere-only standard resolution)
#   - CCCL-SR     (carbon cycle coupled)

# ============================================================
# EC-Earth4 Repository (REQUIRED)
# ============================================================

# Which EC-Earth4 version to use
repo_owner: ec-earth
repo_branch: v4.1.6
# Use specific release tags:
#   - v4.1.6, v4.1.5, v4.2.0, etc.
#   - Or development branches: main, develop

# ============================================================
# User Settings (FILL IN YOUR VALUES!)
# ============================================================

# Your HPC project/account name
account: bsc32
# Examples:
#   - BSC: bsc32, es01, ba01
#   - ECMWF: spesiexp, spnorclim
#   - CSC: project_2001234

# Your scratch directory (where experiments run)
scratch: /gpfs/scratch/username
# Examples:
#   - BSC MN5: /gpfs/scratch/bsc32/bsc32XXX
#   - ECMWF: /scratch/ms/xx/xxxx
#   - CSC Mahti: /scratch/project_2001234

# Default walltime in hours
walltime: 48
# Adjust based on your typical runs:
#   - Short tests: 1-4 hours
#   - Standard runs: 24-48 hours
#   - Long simulations: 72-168 hours

# ============================================================
# Optional: Experiment Defaults
# ============================================================

# Uncomment to set default recipe (avoid typing --recipe every time)
# recipe: gcm-sr.yml
# Common recipes:
#   - gcm-sr.yml    (coupled GCM)
#   - omip-sr.yml   (ocean-only)
#   - amip-sr.yml   (atmosphere-only)
#   - ccycle-sr.yml (carbon cycle)

# Uncomment to set default processor count
# sim_procs: 1120
# Common values:
#   - 1120 (10 nodes on MN5 for CPLD-SR)
#   - 224  (2 nodes on MN5 for OMIP-SR)
#   - 896  (8 nodes on MN5 for AMIP-SR)

# Uncomment to set default experiment ID prefix
# expid: test001
# Useful if you have a naming convention

# ============================================================
# Usage Examples
# ============================================================
#
# With defaults set, you only need to specify experiment-specific params:
#
#   ./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid run001
#
# Or with recipe/sim_procs also set above:
#
#   ./ece4-exp generate --expid run001
#
# Override any default on command line:
#
#   ./ece4-exp generate --recipe omip-sr.yml --walltime 72 --expid long-run
#
"""

    try:
        defaults_file.write_text(example_content)
        print()
        log_info(f"✓ Configuration file created: {COLOR_CYAN}{defaults_file}{COLOR_NC}")
        print()
        print("=" * 70)
        print(" What's in the configuration file?")
        print("=" * 70)
        print()
        print("Platform settings:")
        print("  • platform: Your HPC (bsc-marenostrum5, ecmwf-hpc2020, etc.)")
        print("  • account: Your project/account name")
        print("  • repo_owner, repo_branch: Which EC-Earth4 version to use")
        print()
        print("Optional defaults:")
        print("  • walltime: Default job walltime in hours")
        print("  • recipe: Skip --recipe flag if you always use the same one")
        print("  • sim_procs: Skip --sim-procs flag for standard configs")
        print()
        print("=" * 70)
        print(" How defaults are used")
        print("=" * 70)
        print()
        print("Priority (later overrides earlier):")
        print(f"  1. Defaults file ({COLOR_CYAN}~/.config/ece4-exp/defaults.yml{COLOR_NC})")
        print(f"  2. CLI flags (e.g., {COLOR_CYAN}--platform ecmwf-hpc2020{COLOR_NC})")
        print()
        print("Example:")
        print(f"  Config has: {COLOR_CYAN}platform: bsc-marenostrum5{COLOR_NC}")
        print(f"  Command: {COLOR_CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120{COLOR_NC}")
        print(f"  → Uses platform from config (bsc-marenostrum5)")
        print()
        print(f"  Command: {COLOR_CYAN}./ece4-exp generate --recipe gcm-sr.yml --platform ecmwf-hpc2020{COLOR_NC}")
        print(f"  → Overrides with CLI flag (ecmwf-hpc2020)")
        print()

        # Validate the default content we just wrote
        print("=" * 70)
        print(" Checking placeholder values")
        print("=" * 70)
        print()
        from .yaml_util import load_yaml
        try:
            config = load_yaml(str(defaults_file))

            # Validate scratch path
            scratch_warnings = validate_scratch_path(config.get("scratch"))
            for warning in scratch_warnings:
                log_warn(warning)

            # Validate account
            account_warnings = validate_account(config.get("account"))
            for warning in account_warnings:
                log_warn(warning)

            if scratch_warnings or account_warnings:
                print()
                log_info(f"Next step: Edit the configuration file")
                print(f"  {COLOR_CYAN}nano {defaults_file}{COLOR_NC}")
                print()
                log_info("Or use interactive setup:")
                print(f"  {COLOR_CYAN}./setup.sh --interactive{COLOR_NC}")
            else:
                log_info("Configuration looks good! You can now generate experiments.")
                print(f"  {COLOR_CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test{COLOR_NC}")
        except Exception as e:
            log_warn(f"Could not validate config: {e}")

        print()

    except Exception as e:
        log_error(f"Failed to create defaults file: {e}")
        sys.exit(1)

def main():
    """Command-line entry point."""
    init_user_config()

if __name__ == "__main__":
    main()
