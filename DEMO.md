# ece4-exp Demo Script

**Duration:** 5-10 minutes
**Target:** EC-Earth4 users who want easier experiment configuration

---

## Demo Setup (Before Presenting)

```bash
cd ~/ece4-exp
# Ensure clean state
rm -f *_experiment.yml
```

---

## Part 1: The Problem (1 min)

**SAY:** "Let's say I want to run a standard coupled GCM experiment on MareNostrum 5."

**Show vanilla EC-Earth4 approach:**

```bash
cd ~/ecearth4/scripts/runtime
ls -lh experiment-config-example.yml
# 257 lines!

head -50 experiment-config-example.yml
```

**SAY:** "I need to edit this 257-line YAML file. I must:"
- Set correct component list: `[oifs, xios, nemo, rnfm, oasis]`
- Match grids: TL255L91 + eORCA1L75_ISO
- Calculate processor distribution for 10 nodes
- Set platform paths, SLURM account, walltime...
- Hope I didn't make typos or wrong combinations

**SAY:** "This takes 2-4 hours for new users. There must be a better way!"

---

## Part 2: Enter ece4-exp (1 min)

**SAY:** "Let me show you ece4-exp - it generates these configs automatically."

**Show setup:**
```bash
cd ~/ece4-exp

# First time? One command setup:
./setup.sh
# (if already set up, skip this)
```

**SAY:** "Setup creates `~/.config/ece4-exp/defaults.yml` with your HPC account, platform, etc. You set this ONCE."

```bash
cat ~/.config/ece4-exp/defaults.yml
```

**HIGHLIGHT:**
- `platform: bsc-marenostrum5`
- `account: bsc32`
- `scratch: /gpfs/scratch/username`

---

## Part 3: List Available Recipes (30 sec)

**SAY:** "ece4-exp comes with ready-to-use recipes for common experiment types."

```bash
./ece4-exp list
```

**SHOW OUTPUT:**
- `gcm-sr.yml` - Coupled GCM
- `omip-sr.yml` - Ocean-only
- `amip-sr.yml` - Atmosphere-only
- `ccycle-sr.yml` - Carbon cycle

**SAY:** "Each recipe is a pre-tested configuration for a specific experiment type."

---

## Part 4: Generate a Config (1 min)

**SAY:** "Let's generate a GCM experiment config. Watch how simple this is:"

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid demo001 \
  --dry-run
```

**PAUSE at output, HIGHLIGHT:**
- ✓ Platform: bsc-marenostrum5 (from your defaults)
- ✓ Account: bsc32 (from your defaults)
- ✓ Components: OIFS + NEMO + LPJG (from recipe)
- ✓ Grids: TL255L91 + eORCA1L75_ISO (from recipe)
- ✓ Nodes: 10 (calculated from 1120 procs)
- ✓ Platform config from ECE4 repo (ini_dir, repo_dir)

**SAY:** "30 seconds. That's it. No manual editing needed."

---

## Part 5: What Did It Generate? (1 min)

**Remove `--dry-run` to actually create the file:**

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid demo001
```

---

## Command Reference: All Available Commands

### 1. `list` - Browse Available Recipes

```bash
# List all recipes
./ece4-exp list
```

**Output:**
- Shows standard recipes (gcm-sr, omip-sr, amip-sr, etc.)
- Shows weekly test recipes
- Helps you discover what's available

---

### 2. `info` - Check Current Configuration

```bash
# Show current settings
./ece4-exp info
```

**Shows:**
- Platform, repo branch, launcher settings from `~/.config/ece4-exp/defaults.yml`
- What parameters you still need to provide
- Great for debugging "why isn't my default working?"

**Use case:** Before generating, verify your user config is loaded correctly.

---

### 3. `init-user` - Setup User Configuration

```bash
# Create user config file with prompts
./ece4-exp init-user
```

**What it does:**
- Creates `~/.config/ece4-exp/defaults.yml`
- Prompts for: platform, account, scratch, repo settings
- One-time setup, then all generates use these defaults

**Use case:** First-time setup or switching platforms.

---

### 4. `generate` - Create Experiment Config

#### Basic Usage
```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid myexp
```

#### With All Options
```bash
./ece4-exp generate \
  --platform bsc-marenostrum5 \
  --launcher slurm-wrapper-taskset \
  --kind CPLD-SR \
  --sim-procs 1120 \
  --recipe gcm-sr.yml \
  --repo-owner ec-earth \
  --repo-branch v4.1.6 \
  --expid myexp001 \
  --scratch /gpfs/scratch/user \
  --account bsc32 \
  --walltime 48 \
  --description "My test experiment" \
  --output myexp.yml
```

#### Preview Without Writing
```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --dry-run
```

**Use cases:**
- `--dry-run`: Preview config before creating file
- `-o custom.yml`: Create multiple configs with different names
- Override defaults: Specify flags to override `~/.config/ece4-exp/defaults.yml`

---

### 5. `validate` - Check Configuration

```bash
# Validate a config file
./ece4-exp validate myexp.yml

# Validate default output
./ece4-exp validate
```

**What it checks:**
- YAML syntax
- Required fields present
- Valid component combinations
- Schema compliance

**Use case:** After manual edits, verify config is still valid.

---

### 6. `save` - Save as Recipe

```bash
# After generating and editing experiment.yml
./ece4-exp save experiment.yml my-custom-recipe

# Without args, saves default experiment.yml
./ece4-exp save
```

**What it does:**
- Extracts changes from base config
- Saves as a reusable recipe in `recipes/`
- Great for creating team-specific templates

**Use case:** You tuned an experiment, now save it for reuse.

---

## Usage Patterns

### Pattern 1: Quick Generation (User Config Set Up)
```bash
# After running init-user once
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid exp001
```

### Pattern 2: One-Off Different Settings
```bash
# Override platform for this run only
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --platform ecmwf-hpc2020 \
  --account spesimon
```

### Pattern 3: Create Multiple Configs
```bash
# Generate multiple experiments with different settings
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid ctrl -o ctrl.yml
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid pert --walltime 72 -o pert.yml
./ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid ocean -o ocean.yml
```

### Pattern 4: Development Workflow
```bash
# 1. Generate base config
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 -o dev.yml

# 2. Edit manually
vim dev.yml

# 3. Validate changes
./ece4-exp validate dev.yml

# 4. Save as new recipe (optional)
./ece4-exp save dev.yml my-tuned-gcm
```

### Pattern 5: Autosubmit Mode (Backward Compatibility)
```bash
# For auto-ecearth4 users
./ece4-exp generate \
  --expdef expdef_a001.yml \
  --jobs jobs_a001.yml
```

---

**Check the output:**
```bash
ls -lh demo001_experiment.yml
# Show it's a real config file

head -30 demo001_experiment.yml
```

**HIGHLIGHT key sections:**
```bash
# Show components are set
grep "components:" demo001_experiment.yml

# Show grids are correct
grep "grid:" demo001_experiment.yml

# Show account is set
grep "account:" demo001_experiment.yml

# Show ini_dir is set (from upstream platform config!)
grep "ini_dir:" demo001_experiment.yml
```

**SAY:** "This is a complete, validated configuration ready to use with EC-Earth4."

---

## Part 6: Validate It (30 sec)

**SAY:** "Before running, let's validate it catches any errors:"

```bash
./ece4-exp validate demo001_experiment.yml
```

**SHOW:** Clean validation (no errors)

**SAY:** "If there were typos, wrong component combinations, or missing fields, it would catch them here - before waiting 2 hours in the queue!"

---

## Part 7: Use with EC-Earth4 (1 min)

**SAY:** "Now use it with standard EC-Earth4 workflow:"

```bash
cd ~/ecearth4/scripts/runtime

se my-user-config.yml \
   ../platforms/bsc-marenostrum5-intel+openmpi.yml \
   ~/ece4-exp/demo001_experiment.yml \
   scriptlib/main.yml
```

**SAY:** "The experiment would start normally. ece4-exp just made creating that experiment-config.yml painless."

---

## Part 8: Other Experiment Types (2 min)

**SAY:** "Let's try different experiment types to show the flexibility."

### 8a. Ocean-Only Run

```bash
cd ~/ece4-exp

./ece4-exp generate \
  --recipe omip-sr.yml \
  --sim-procs 224 \
  --expid omip001 \
  --dry-run
```

**HIGHLIGHT:**
- Different components: NEMO + XIOS (no atmosphere!)
- Different processor count: 224 (2 nodes)
- Forcing: ERA5 atmospheric forcing configured

**SAY:** "Perfect for ocean-only sensitivity studies."

---

### 8b. High-Resolution Run

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 2240 \
  --expid gcm-hr \
  --walltime 72 \
  --dry-run
```

**HIGHLIGHT:**
- More processors: 2240 (20 nodes)
- Longer walltime: 72 hours
- Same component setup, just scaled up

**SAY:** "Scale up or down easily. The tool calculates optimal processor distribution."

---

### 8c. Carbon Cycle Run

```bash
./ece4-exp generate \
  --recipe ccycle-sr.yml \
  --sim-procs 1120 \
  --expid carbon001 \
  --dry-run
```

**HIGHLIGHT:**
- Components include LPJG (vegetation) + PISCES (ocean biogeochemistry)
- CO2 coupling configured
- Processor layout optimized for LPJG

**SAY:** "Complex configurations made simple."

---

## Part 9: The Smart Part - Layering (1 min)

**SAY:** "How does it work? Smart layering system:"

**DRAW/SHOW diagram:**

```
┌─────────────────────────────────────┐
│ 1. Base (from ECE4 git)            │ ← experiment-config-example.yml
│    └─ All possible parameters      │
├─────────────────────────────────────┤
│ 2. Platform (from ECE4 git)        │ ← bsc-marenostrum5-intel+openmpi.yml
│    └─ ini_dir, repo_dir, cpus/node│
├─────────────────────────────────────┤
│ 3. Launcher (local)                │ ← Processor layouts per experiment type
│    └─ Job configs, node allocation │
├─────────────────────────────────────┤
│ 4. Recipe (your science)           │ ← gcm-sr.yml
│    └─ Components, grids, forcing   │
├─────────────────────────────────────┤
│ 5. Your overrides (CLI/defaults)   │ ← --expid, --account, --walltime
│    └─ Experiment-specific params   │
└─────────────────────────────────────┘
         ↓
    demo001_experiment.yml (ready!)
```

**SAY:** "Each layer adds or overrides the previous. You only specify what changes."

---

## Part 10: Reproducibility (1 min)

**SAY:** "Let's say you've tuned a perfect configuration and want to share it."

**Simulate editing:**
```bash
# Imagine you manually edited demo001_experiment.yml
# and changed some parameters for your specific study
```

**Extract recipe:**
```bash
./ece4-exp save \
  --recipe gcm-sr.yml \
  my-tuned-gcm.yml
```

**Show the extracted recipe:**
```bash
cat my-tuned-gcm.yml
```

**SAY:** "This saves ONLY your changes - a minimal, shareable recipe. Colleagues can reproduce your exact setup with one command."

---

## Part 11: Summary & Next Steps (1 min)

**SAY:** "To recap:"

✅ **Setup once:** `./setup.sh` (2 minutes)
✅ **Use forever:** `./ece4-exp generate --recipe X --sim-procs Y --expid Z`
✅ **Share science:** Extract minimal recipes
✅ **Catch errors:** Validation before submission
✅ **Flexible:** Override anything on CLI

**Show resources:**

```bash
# Documentation
cat README.md | head -50

# Available recipes
ls recipes/
ls recipes/weekly_tests/

# Your config
cat ~/.config/ece4-exp/defaults.yml
```

**SAY:** "Questions? Try it yourself:"

```
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
./setup.sh
```

---

## Bonus: Quick Tips

### Tip 1: Dry-Run First
Always use `--dry-run` to preview before generating:
```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test --dry-run
```

### Tip 2: Check What's Available
```bash
./ece4-exp list          # Recipes
./ece4-exp --help        # All options
```

### Tip 3: Override Defaults
```bash
./ece4-exp generate \
  --recipe omip-sr.yml \
  --sim-procs 224 \
  --expid quick-test \
  --walltime 2 \           # Override default 48h
  --scratch /tmp/test      # Override default scratch
```

### Tip 4: Share Recipes
```bash
# Save your tweaked config
./ece4-exp save my-experiment.yml

# Share with team
cp my-experiment.yml recipes/team/
git add recipes/team/my-experiment.yml
```

---

## Common Questions & Answers

**Q: Does this replace manual editing?**
A: No - it generates a great starting point. You can always edit the output YAML if needed.

**Q: What if I need a custom setup?**
A: Start with the closest recipe, generate, then manually edit. Or create your own recipe!

**Q: Does it work on other platforms?**
A: Yes! Supports BSC, ECMWF, CSC, DKRZ. Platform configs come from upstream EC-Earth4 repo.

**Q: Is it maintained?**
A: Yes - platform configs are fetched from EC-Earth4 repository, so always in sync.

**Q: What about Autosubmit users?**
A: Backward compatible! Still works with `--expdef` and `--jobs` flags.

---

## Demo Cleanup

```bash
# Remove demo files
rm -f demo001_experiment.yml
rm -f omip001_experiment.yml
rm -f my-tuned-gcm.yml
```

---

## Presentation Tips

1. **Start with empathy**: Everyone has struggled with YAML configs
2. **Show, don't tell**: Run commands live, show actual output
3. **Highlight time savings**: "2-4 hours → 30 seconds"
4. **Use realistic examples**: GCM, OMIP scenarios users recognize
5. **Address concerns**: "Can I still edit manually?" (Yes!)
6. **End with call to action**: "Try it this week!"

**Good luck! 🚀**
