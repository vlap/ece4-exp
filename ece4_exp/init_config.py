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

def init_user_config():
    """Create ~/.config/ece4-exp/ with example defaults."""
    config_dir = paths.USER_CONFIG_DIR
    defaults_file = paths.USER_DEFAULTS_FILE

    # Create directory if it doesn't exist
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Created config directory: {config_dir}")
    else:
        log_info(f"Config directory already exists: {config_dir}")

    # Create example defaults file if it doesn't exist
    if defaults_file.exists():
        log_warn(f"Defaults file already exists: {defaults_file}")
        log_info("To reconfigure, edit the file or delete it and run init again.")
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
        log_info(f"Created example defaults file: {COLOR_CYAN}{defaults_file}{COLOR_NC}")
        print()
        log_info("Edit this file to set your personal defaults, then run:")
        print(f"  {COLOR_CYAN}./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid myexp{COLOR_NC}")
        print()
    except Exception as e:
        log_error(f"Failed to create defaults file: {e}")
        sys.exit(1)

def main():
    """Command-line entry point."""
    init_user_config()

if __name__ == "__main__":
    main()
