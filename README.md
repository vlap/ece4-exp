# ece4-exp: EC-Earth4 Experiment Configuration Tool

Standalone tool for managing EC-Earth4 experiment configurations using a modular YAML overlay system.

## Overview

`ece4-exp` helps you generate EC-Earth4 experiment configuration files by:
- Fetching base configs from the EC-Earth4 repository
- Applying platform-specific settings (from upstream ECE4 repo)
- Merging experiment recipes (component configurations, forcing options)
- Adding your user-specific parameters (account, scratch path, etc.)

**No Autosubmit dependency required** - works standalone with explicit CLI parameters.

## Quick Start

### One-Command Setup

```bash
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
./setup.sh
```

This will:
- ✓ Check Python dependencies
- ✓ Install required packages
- ✓ Create user configuration
- ✓ Install bash completion (optional)
- ✓ Test the installation

Then edit `~/.config/ece4-exp/defaults.yml` with your HPC account and paths.

### Interactive Setup (Recommended for First-Time Users)

```bash
./setup.sh --interactive
```

Guides you through configuration with prompts.

### Manual Setup

```bash
pip install -r requirements.txt
./ece4-exp init-user
# Edit ~/.config/ece4-exp/defaults.yml
```

### 3. Generate Experiment Config

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid myexp001 \
  --dry-run
```

With user defaults set, you only need to specify experiment-specific parameters!

### 4. Use with EC-Earth4

```bash
cd /path/to/ecearth4/scripts/runtime
se user-config.yml \
   ../platforms/bsc-marenostrum5-intel+openmpi.yml \
   /path/to/myexp001_experiment.yml \
   scriptlib/main.yml
```

## Features

### YAML Overlay System

Configurations are merged in this order:
1. **Base** (from EC-Earth4 repo: `experiment-config-example.yml`)
2. **Platform config** (from EC-Earth4 repo: `scripts/platforms/*.yml`)
3. **Launcher config** (local: `platforms/*/launchers.yml`)
4. **Recipe** (experiment pattern: `recipes/*.yml`)
5. **User overrides** (CLI parameters or user defaults)

### User Configuration

Store your defaults in `~/.config/ece4-exp/defaults.yml`:

```yaml
platform: bsc-marenostrum5
launcher: slurm-wrapper-taskset
repo_owner: ec-earth
repo_branch: v4.1.6
account: bsc32
scratch: /gpfs/scratch/username
walltime: 48
```

Then generate experiments with minimal parameters:
```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test
```

### Recipe Collection

Pre-built recipes for common experiment types:
- `gcm-sr.yml` - Coupled GCM (OIFS + NEMO + LPJG)
- `amip-sr.yml` - Atmosphere-only with prescribed SSTs
- `omip-sr.yml` - Ocean-only forced run
- `ccycle-sr.yml` - Carbon cycle configuration

Create your own recipes by saving configuration deltas!

## Commands

```bash
./ece4-exp <command> [options]

Commands:
  init-user   Create user configuration directory
  generate    Generate experiment configuration
  validate    Validate experiment YAML
  list        List available recipes
  save        Extract recipe from experiment config
  info        Show configuration (for autosubmit users)
```

## Parameters

### Core Parameters
- `--platform` - HPC platform (e.g., `bsc-marenostrum5`, `ecmwf-hpc2020`)
- `--launcher` - Job launcher (e.g., `slurm-wrapper-taskset`)
- `--sim-procs` - Number of simulation processors
- `--recipe` - Recipe file (e.g., `gcm-sr.yml`)
- `--repo-owner`, `--repo-branch` - EC-Earth4 repo to fetch configs from

### User Parameters
- `--expid` - Experiment ID
- `--scratch` - Scratch directory path
- `--account` - HPC account/project
- `--walltime` - Walltime in hours
- `--description` - Experiment description

### Output Control
- `--dry-run` - Preview without writing file
- `--output` - Output filename (default: `experiment.yml`)

## Directory Structure

```
ece4-exp/
├── ece4-exp              # Main CLI script
├── ece4_exp/             # Python package
│   ├── generate-experiment-config.py
│   ├── validate-experiment-config.py
│   ├── init_config.py
│   └── yaml_util.py
├── recipes/              # Experiment recipes
│   ├── gcm-sr.yml
│   └── weekly_tests/
├── platforms/            # Platform launcher configs
│   ├── bsc-marenostrum5/
│   └── ecmwf-hpc2020/
└── templates/            # Utilities
    └── ece4-exp-completion.sh
```

## Autosubmit Compatibility

For backward compatibility, autosubmit mode still works:

```bash
./ece4-exp generate \
  --expdef /path/to/expdef_EXPID.yml \
  --jobs /path/to/jobs_EXPID.yml
```

Parameters are resolved in order: **CLI args > user config > autosubmit files**

## Examples

### Standard Coupled Run
```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid gcm001
```

### High-Resolution AMIP
```bash
./ece4-exp generate \
  --recipe amip-sr.yml \
  --sim-procs 896 \
  --expid amip_hr \
  --walltime 72
```

### Ocean-Only Forced Run
```bash
./ece4-exp generate \
  --recipe omip-sr.yml \
  --sim-procs 224 \
  --expid omip_test
```

## Contributing

See the EC-Earth4 documentation for details on experiment configuration parameters and ScriptEngine usage.
