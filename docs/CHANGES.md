# Changelog: ece4-recipe → ece4-exp

## Major Refactoring (June 2026)

### Name Change
- **ece4-recipe** → **ece4-exp** (experiment configuration tool)
- Module: `ece4_recipe/` → `ece4_exp/`
- User config: `~/.config/ece4-recipe/` → `~/.config/ece4-exp/`

### Architecture Simplification

**Removed Autosubmit dependency:**
- Tool works standalone with explicit CLI parameters
- Autosubmit mode retained for backward compatibility
- Resolution order: CLI args > user config > autosubmit files

**New layering system:**
1. Base (from ECE4 git: `experiment-config-example.yml`)
2. Platform config (from ECE4 git: `scripts/platforms/*.yml`)
3. Launcher config (local: `platforms/*/launchers.yml`)
4. Recipe (experiment pattern)
5. User overrides (CLI params)

### Integration with EC-Earth4 Repository

**Sparse checkout enhanced:**
- Now fetches both `experiment-config-example.yml` AND `scripts/platforms/*.yml`
- Platform configs provide: `ini_dir`, `repo_dir`, `cpus_per_node`, SLURM defaults
- Removes duplication - single source of truth from upstream

**Removed local duplication:**
- Deleted `configs/asconf_vars.yml` (superseded by ECE4 platform files)
- Removed `ini_dir` from local `launchers.yml` (now from ECE4 platform files)

### New Features

**User configuration:**
- `~/.config/ece4-exp/defaults.yml` for personal defaults
- Set once: platform, account, scratch, repo settings
- Generate experiments with minimal parameters

**New CLI parameters:**
- `--expid` - Experiment ID
- `--scratch` - Scratch directory
- `--account` - HPC account
- `--walltime` - Walltime in hours
- `--description` - Experiment description

### Directory Structure Changes

**Before:**
```
ece4-recipe/
├── ece4-recipe.sh
├── ece4_recipe/
├── configs/
│   ├── asconf_vars.yml
│   └── compilation.yml
├── templates/
│   ├── bsc32_platforms.yml
│   ├── hpc2020_platforms.yml
│   ├── ecearth4_user_config.yml
│   └── ece4-recipe-completion.sh
└── ...
```

**After:**
```
ece4-exp/
├── ece4-exp (renamed, no .sh suffix)
├── ece4_exp/
├── scripts/
│   └── ece4-exp-completion.sh
├── docs/
│   ├── autosubmit/ (moved autosubmit-specific files)
│   ├── examples/
│   └── presentation/
└── ...
```

### Files Reorganized
- `configs/asconf_vars.yml` → `templates/autosubmit/` (autosubmit templates)
- `configs/compilation.yml` → `templates/autosubmit/` (autosubmit templates)
- `templates/` → reorganized: bash completion → `scripts/`, autosubmit configs → `templates/autosubmit/`
- `docs/examples/` now only contains actual experiment config examples
- `ece4_exp/init-user-conf.py` → replaced by `init_config.py`
- `ece4_exp/unknown_experiment_pristine.yml` → removed (dead file)

### Code Improvements

**Maintainability:**
- Added docstrings to key functions
- Consistent error messages
- Better validation and helpful hints
- Cleaner separation of concerns

**Future-proofing:**
- Platform files from upstream ECE4 repo (auto-updated)
- Flexible platform matching (handles compiler variants)
- Extensible user config system
- Clear fallback hierarchy

## Migration Guide

### For Standalone Users (NEW)

1. Install and setup:
```bash
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
pip install -r requirements.txt
./ece4-exp init-user
# Edit ~/.config/ece4-exp/defaults.yml
```

2. Generate experiments:
```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid myexp
```

### For Autosubmit Users (BACKWARD COMPATIBLE)

No changes needed! Your existing commands still work:
```bash
./ece4-exp generate --expdef expdef_test.yml --jobs jobs_test.yml
```

### Updating Scripts

If you have scripts that call `ece4-recipe.sh`, update to:
```bash
# Old
./ece4-recipe.sh generate ...

# New
./ece4-exp generate ...
```

## Benefits

1. **Simpler:** No Autosubmit dependency, clear parameter hierarchy
2. **Maintainable:** Single source of truth (ECE4 platform files from upstream)
3. **Flexible:** User config + CLI overrides for different use cases
4. **Compatible:** Autosubmit mode still works for existing workflows
5. **Future-proof:** Tracks upstream ECE4 platform configurations automatically
