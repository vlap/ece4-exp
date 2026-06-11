# ece4-exp

**Generate EC-Earth4 experiment configs in 30 seconds.**

```bash
pip install ece4-exp
ece4-exp setup                 # First-time setup
ece4-exp generate gcm-sr 10 a001  # 10 nodes
```

## Quick Start

```bash
# 1. Install
pip install ece4-exp

# 2. Setup (also enables TAB completion)
ece4-exp setup
# Restart your shell

# 3. Generate experiment
ece4-exp generate gcm-sr 10 a001  # 10 nodes = 1120 cores on MareNostrum5
```

That's it! You have `a001_experiment.yml` ready to use with EC-Earth4.

## Common Recipes

| Recipe | Description | Typical Nodes (MN5) |
|--------|-------------|---------------------|
| `gcm-sr` | Coupled atmosphere-ocean GCM | 10 nodes (1120 cores) |
| `omip-sr` | Ocean-only forced by reanalysis | 2 nodes (224 cores) |
| `amip-sr` | Atmosphere-only prescribed SST | 8 nodes (896 cores) |
| `ccycle-sr` | Carbon cycle coupled | 10+ nodes |

## Commands

```bash
# Setup
ece4-exp setup                     # Configure platform and account

# Generate (specify nodes, not processors)
ece4-exp generate RECIPE NODES EXPID
ece4-exp generate gcm-sr 10 a001     # 10 nodes
ece4-exp generate omip-sr 2 o001 --walltime 72

# Discovery
ece4-exp list                      # Show available recipes
ece4-exp inspect gcm-sr            # View recipe details

# Advanced
ece4-exp save --expid a001         # Save modifications as new recipe
```

## Customization

**Override defaults:**
```bash
ece4-exp generate gcm-sr 10 a001 --platform ecmwf-hpc2020 --account myproj
```

**Custom recipes:**
```bash
# Generate, edit, save as recipe
ece4-exp generate gcm-sr 10 test
vim test_experiment.yml              # Make changes
ece4-exp save --expid test --recipe gcm-sr
# If you moved the file: --config /path/to/test_experiment.yml

# Reuse your recipe
ece4-exp generate test 10 a002
```

**Custom platforms:**
```bash
cp $(python3 -c "from ece4_exp import paths; print(paths.PLATFORMS_DIR)")/bsc-marenostrum5.yml \\
   ~/.config/ece4-exp/platforms/my-hpc.yml
vim ~/.config/ece4-exp/platforms/my-hpc.yml  # Adjust settings
ece4-exp generate gcm-sr 10 a001 --platform my-hpc
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

## Tab Completion

Add one line to your shell config file (shown by `ece4-exp setup`):

**bash** — add to `~/.bashrc`:
```bash
eval "$(register-python-argcomplete ece4-exp)"
```

**zsh** — add to `~/.zshrc`:
```bash
eval "$(register-python-argcomplete ece4-exp)"
```

Then restart your shell or run `source ~/.bashrc` (or `~/.zshrc`).

After that:
- `ece4-exp ge<TAB>` → `ece4-exp generate`
- `ece4-exp generate gcm<TAB>` → completes recipe names

## Support

- **Issues:** https://github.com/vlap/ece4-exp/issues
- **Contact:** vladimir.lapin@bsc.es
- **License:** MIT
