# ece4-exp

**Generate EC-Earth4 experiment configs in 30 seconds.**

```bash
pip install ece4-exp
ece4-exp setup                    # First-time setup
ece4-exp generate gcm-sr 1120 a001
```

## Quick Start

```bash
# 1. Install
pip install ece4-exp

# 2. Configure (platform, account)
ece4-exp setup

# 3. Generate experiment
ece4-exp generate gcm-sr 1120 a001
```

That's it! You have `a001_experiment.yml` ready to use with EC-Earth4.

## Common Recipes

| Recipe | Description | Typical Procs (MN5) |
|--------|-------------|---------------------|
| `gcm-sr` | Coupled atmosphere-ocean GCM | 1120 (10 nodes) |
| `omip-sr` | Ocean-only forced by reanalysis | 224 (2 nodes) |
| `amip-sr` | Atmosphere-only prescribed SST | 896 (8 nodes) |
| `ccycle-sr` | Carbon cycle coupled | 1120+ |

## Commands

```bash
# Setup
ece4-exp setup                     # Configure platform and account

# Generate
ece4-exp generate RECIPE PROCS EXPID
ece4-exp generate gcm-sr 1120 a001
ece4-exp generate omip-sr 224 o001 --walltime 72

# Discovery
ece4-exp list                      # Show available recipes
ece4-exp inspect gcm-sr            # View recipe details

# Advanced
ece4-exp save --expid a001         # Save modifications as new recipe
```

## Customization

**Override defaults:**
```bash
ece4-exp generate gcm-sr 1120 a001 --platform ecmwf-hpc2020 --account myproj
```

**Custom recipes:**
```bash
# Save your modifications
ece4-exp generate gcm-sr 1120 test
vim test_experiment.yml            # Make changes
ece4-exp save --expid test         # Saves to ~/.config/ece4-exp/recipes/test.yml

# Reuse your recipe
ece4-exp generate test 1120 a002
```

**Custom platforms:**
```bash
cp platforms/bsc-marenostrum5.yml ~/.config/ece4-exp/platforms/my-hpc.yml
vim ~/.config/ece4-exp/platforms/my-hpc.yml  # Adjust node layouts
ece4-exp generate gcm-sr 1120 a001 --platform my-hpc
```

## What It Does

**ece4-exp** creates EC-Earth4 experiment configuration files by combining:

1. **Base config** (from EC-Earth4 repo)
2. **Platform settings** (HPC-specific paths, modules)
3. **Recipe** (experiment type: GCM, OMIP, AMIP, etc.)
4. **Your defaults** (~/.config/ece4-exp/defaults.yml)
5. **CLI overrides** (command-line flags)

The result is a validated YAML file you pass to EC-Earth4's runtime script:

```bash
cd /path/to/ecearth4/scripts/runtime
se user.yml platform.yml a001_experiment.yml scriptlib/main.yml
```

## Documentation

- **Full guide:** https://ece4-exp.readthedocs.io
- **Help:** `ece4-exp --help` or `ece4-exp generate --help`

## Tab Completion (Optional)

```bash
# Bash
echo 'eval "$(ece4-exp completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(ece4-exp completion zsh)"' >> ~/.zshrc
```

Now: `ece4-exp ge<TAB>` → `ece4-exp generate`

## Support

- **Issues:** https://github.com/vlap/ece4-exp/issues
- **Contact:** vladimir.lapin@bsc.es
- **License:** MIT
