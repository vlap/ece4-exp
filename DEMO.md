# ece4-exp Demo Guide

**Duration:** 10 minutes  
**Target:** EC-Earth4 users who want easier experiment configuration

---

## The Problem

Configuring EC-Earth4 experiments manually is time-consuming:
- Edit 257-line YAML files
- Match components, grids, processor counts
- Set platform paths, SLURM settings
- Easy to make mistakes

**Result:** 2-4 hours for experienced users, longer for newcomers

---

## The Solution: ece4-exp

One command generates production-ready configs:

```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid myexp
```

You get:
- Correct component configuration
- Calculated node layout
- Validated and ready to run

---

## Quick Demo

Run the interactive demo to see it in action:

```bash
./QUICK_DEMO.sh
```

This demonstrates:
1. **list** - Browse available recipes
2. **generate** - Create experiment configs
3. **inspect** - Check what was generated
4. **save** - Save customizations as new recipes
5. **validate** - Verify configurations
6. **Different types** - GCM, OMIP, etc.

---

## Command Reference

### 1. `list` - Browse Available Recipes

```bash
./ece4-exp list
```

Shows all available recipes (gcm-sr, omip-sr, amip-sr, ccycle-sr, etc.)

### 2. `init-user` - Setup User Configuration

```bash
./ece4-exp init-user
```

Creates `~/.config/ece4-exp/defaults.yml` with your settings:
- Platform, account, scratch path
- Default walltime, repo branch
- One-time setup

### 3. `generate` - Create Experiment Config

**Basic usage:**
```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid myexp
```

**With all options:**
```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid myexp001 \
  --account bsc32 \
  --walltime 48 \
  --description "My test experiment" \
  --output myexp.yml
```

**Preview without writing:**
```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --dry-run
```

### 4. `validate` - Check Configuration

```bash
./ece4-exp validate myexp.yml
```

Checks:
- YAML syntax
- Required fields
- Valid component combinations
- Schema compliance

### 5. `save` - Save as Recipe

After editing an experiment config:

```bash
# Modify your config
vim myexp.yml

# Save changes as new recipe
./ece4-exp save --expid myexp -o my-custom-recipe.yml
```

Creates a minimal recipe with only your changes.

### 6. `info` - Check Current Configuration

```bash
./ece4-exp info
```

Shows your current defaults from `~/.config/ece4-exp/defaults.yml`

---

## Real-World Examples

### Example 1: Standard Coupled GCM

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid gcm001
```

**Result:** OIFS + NEMO + XIOS + OASIS, 10 nodes, TL255L91 + eORCA1L75

### Example 2: Ocean-Only Forced Run

```bash
./ece4-exp generate \
  --recipe omip-sr.yml \
  --sim-procs 224 \
  --expid omip001
```

**Result:** NEMO + XIOS only, 2 nodes, ERA5 forcing

### Example 3: Create Multiple Configs

```bash
# Control run
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \
  --expid ctrl -o ctrl.yml

# Perturbed run with longer walltime
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \
  --expid pert --walltime 72 -o pert.yml

# Ocean-only
./ece4-exp generate --recipe omip-sr.yml --sim-procs 224 \
  --expid ocean -o ocean.yml
```

### Example 4: Development Workflow

```bash
# 1. Generate base config
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 -o dev.yml

# 2. Edit manually
vim dev.yml

# 3. Validate changes
./ece4-exp validate dev.yml

# 4. Save as new recipe (optional)
./ece4-exp save --expid dev -o my-tuned-gcm
```

---

## Usage Patterns

### Pattern 1: With User Config

After running `./ece4-exp init-user`:

```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid exp001
```

Platform, account, scratch come from your defaults.

### Pattern 2: One-Off Override

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --platform ecmwf-hpc2020 \
  --account spesimon
```

Override defaults for this run only.

### Pattern 3: Autosubmit Mode (Backward Compatibility)

```bash
./ece4-exp generate \
  --expdef expdef_a001.yml \
  --jobs jobs_a001.yml
```

For auto-ecearth4 users.

---

## Tips

**Time savings:**
- Manual config: 2-4 hours
- With ece4-exp: 30 seconds

**Best practices:**
1. Run `init-user` first - set your defaults once
2. Use `--dry-run` to preview before creating files
3. Validate before submitting: `./ece4-exp validate myexp.yml`
4. Save customizations as recipes for reuse

**Getting help:**
```bash
./ece4-exp --help           # Show all commands
./ece4-exp generate --help  # Help for specific command
```

**Resources:**
- `README.md` - Complete guide
- `QUICK_DEMO.sh` - Interactive demo
- `docs/presentation/ece4-exp-intro.pdf` - Slides

---

## Troubleshooting

**"Missing required parameters"**
→ Run `./ece4-exp init-user` to set defaults, or provide via CLI flags

**"Recipe not found"**
→ Run `./ece4-exp list` to see available recipes

**"Platform not found"**
→ Check `platforms/` directory for available platforms

---

## Next Steps

1. **Install:** `git clone && ./setup.sh`
2. **Configure:** `./ece4-exp init-user`
3. **Try demo:** `./QUICK_DEMO.sh`
4. **Generate:** `./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120`
5. **Run:** `se user.yml platform.yml experiment.yml scriptlib/main.yml`

**Questions?** vladimir.lapin@bsc.es
