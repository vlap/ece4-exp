---
marp: true
paginate: true
theme: default
backgroundColor: '#ffffff'
color: '#333'
header: 'ece4-exp: EC-Earth4 Made Simple'
footer: 'Vladimir Lapin (BSC) | June 2026'
style: |
  section {
    font-size: 28px;
    padding: 40px 70px;
  }
  h1 {
    color: #2563eb;
    font-size: 44px;
    margin-bottom: 25px;
  }
  h2 {
    color: #1e40af;
    font-size: 32px;
  }
  code {
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 24px;
  }
  pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 15px;
    border-radius: 8px;
    font-size: 22px;
    line-height: 1.4;
  }
  ul {
    line-height: 1.6;
    margin: 15px 0;
  }
  li {
    margin: 8px 0;
  }
  strong {
    color: #1e40af;
  }
  p {
    margin: 12px 0;
  }
  table {
    font-size: 22px;
    margin: 15px 0;
  }
---

<!-- _class: lead -->

# ece4-exp

## EC-Earth4 Experiment Configuration Made Simple

**From hours of YAML editing to 30 seconds**

---

# The Problem

**Creating an EC-Earth4 experiment config is painful:**

- 📝 Edit 257-line YAML file manually
- 🧮 Calculate node layouts and processor distribution
- 🔧 Match components, grids, platform paths
- ⚠️ Easy to make mistakes (typos, incompatible combinations)
- ⏱️ Repeat for every experiment

**Result:** 2-4 hours for experienced users, longer for newcomers

---

# The Solution

**One command generates production-ready configs:**

```bash
ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid my-experiment
```

**That's it.** You get:
- ✅ Correct component configuration (OIFS + NEMO + XIOS + OASIS)
- ✅ Calculated node layout (10 nodes, 112 procs/node)
- ✅ Platform paths from upstream EC-Earth4 repo
- ✅ Validated and ready to run

**Time saved:** ~3.5 hours per experiment

---

# Pre-Built Recipes

**Ready-to-use experiment templates:**

| Recipe | Description | Procs | Nodes* |
|--------|-------------|-------|--------|
| `gcm-sr.yml` | Coupled atmosphere-ocean | 1120 | 10 |
| `omip-sr.yml` | Ocean-only with ERA5 forcing | 224 | 2 |
| `amip-sr.yml` | Atmosphere-only (prescribed SST) | 896 | 8 |
| `ccycle-sr.yml` | Carbon cycle (with LPJG) | 1120+ | 10+ |

<sub>*MareNostrum5 (112 cores/node)</sub>

**All recipes:** Tested, validated, production-ready

---

# How It Works

**YAML overlay system** - configurations merged in order:

```
Base config (EC-Earth4 repo)
  ↓
+ Platform launcher (local file)
  ↓
+ Recipe (experiment pattern)
  ↓
+ Your CLI parameters
  ↓
= Generated config (229 lines)
```

**Smart features:**
- Auto-fetches latest base config from EC-Earth4 repo
- Auto-calculates processor distribution
- Validates before you submit

---

# Real Examples

**Coupled atmosphere-ocean (10 nodes):**
```bash
ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120
# → OIFS + NEMO + XIOS + OASIS + RNFM
# → TL255L91 + eORCA1L75
```

**Ocean-only (2 nodes):**
```bash
ece4-exp generate --recipe omip-sr.yml --sim-procs 224
# → NEMO + XIOS (no atmosphere)
# → Forced by ERA5
```

Different science, different resources - **same simple command**.

---

# Setup: Once and Forever

**One-time installation (2 minutes):**
```bash
pip install ece4-exp


```

**Configure your defaults (1 minute):**
```bash
ece4-exp init-user
# Edit ~/.config/ece4-exp/defaults.yml
```

Set your platform, account, scratch path **once**.

**Then just:**
```bash
ece4-exp generate --recipe <type> --sim-procs <n>
```

Override when needed: `--platform ecmwf-hpc2020`

---

# Advanced Features

**Create custom recipes:**
```bash
# Modify generated config
vim myexp.yml

# Save as new recipe
ece4-exp save --expid myexp -o my-recipe.yml

# Reuse it
ece4-exp generate --recipe my-recipe.yml --sim-procs 1120
```

**Scripting support:**
```bash
# Quiet mode (no colors, for scripts)
ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --quiet

# Batch generation
for exp in {001..010}; do
  ece4-exp generate --recipe gcm-sr.yml --expid exp$exp
done
```

---

# Platform Support

**Currently supported:**
- 🇪🇸 BSC MareNostrum 5
- 🇮🇹 ECMWF HPC2020

**Adding a new platform:**
1. Create `platforms/<platform>.yml` with launcher templates
2. Specify `ppn` (processors per node)
3. Done!

**Example:**
```yaml
ppn: 128  # Processors per node
slurm-wrapper-taskset:
  oifs:
    script: "srun --cpus-per-task=1 ..."
```

Small file (~50 lines), platform ready to use.

---

# Get Started

**Try it now:**

```bash
pip install ece4-exp

./QUICK_DEMO.sh  # Interactive 3-minute demo
```

**Documentation:**
- `README.md` - Complete guide
- `DEMO.md` - Walkthrough with examples
- `ece4-exp --help` - Command reference

**Compatible with:**
- ✅ Manual EC-Earth4 workflows (ScriptEngine)
- ✅ Autosubmit (auto-ecearth4) - backward compatible

**Questions?** vladimir.lapin@bsc.es  
**Code:** https://github.com/vlap/ece4-exp
