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
ece4-exp generate gcm-sr 10 a001
```

**That's it.** You get:
- ✅ Correct component configuration (OIFS + NEMO + XIOS + OASIS)
- ✅ Calculated node layout (10 nodes × 112 cores = 1120 procs)
- ✅ Base config fetched from upstream EC-Earth4 repo
- ✅ Validated and ready to run

**Time saved:** ~3.5 hours per experiment

---

# Pre-Built Recipes

**Ready-to-use experiment templates:**

| Recipe | Description | Nodes* | Components |
|--------|-------------|--------|------------|
| `gcm-sr` | Coupled atmosphere-ocean | 10 | OIFS + NEMO + XIOS + OASIS |
| `omip-sr` | Ocean-only with ERA5 forcing | 2 | NEMO + XIOS |
| `amip-sr` | Atmosphere-only (prescribed SST) | 8 | OIFS + XIOS + AMIPFR |
| `ccycle-sr` | Carbon cycle (with LPJG) | 10+ | OIFS + NEMO + LPJG + XIOS |

<sub>*MareNostrum5 (112 cores/node). All at standard resolution: TL255L91 + eORCA1L75.</sub>

**All recipes:** Tested, validated, production-ready

---

# How It Works

**YAML overlay system** - configurations merged in order:

```
1. Base config     (fetched from EC-Earth4 git repo, pinned version)
       ↓
2. Platform        (node layout, SLURM settings for your HPC)
       ↓
3. Recipe          (experiment type: coupled, ocean-only, ...)
       ↓
4. Your defaults   (~/.config/ece4-exp/defaults.yml)
       ↓
5. CLI flags       (per-run overrides)
       ↓
   Generated config (a001_experiment.yml, ~229 lines)
```

You only write what's **different from the defaults**.
The tool handles the rest: node math, platform paths, component config.

---

# Real Examples

**Coupled atmosphere-ocean (10 nodes):**
```bash
ece4-exp generate gcm-sr 10 a001
# → OIFS + NEMO + XIOS + OASIS + RNFM
# → TL255L91 + eORCA1L75
```

**Ocean-only (2 nodes):**
```bash
ece4-exp generate omip-sr 2 o001
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
ece4-exp setup
# Edit ~/.config/ece4-exp/defaults.yml
```

Set your platform, account **once**.

**Then just:**
```bash
ece4-exp generate RECIPE NODES EXPID
```

Override when needed: `--platform ecmwf-hpc2020`

---

# Advanced Features

**Create custom recipes:**
```bash
# Generate and tweak
ece4-exp generate gcm-sr 10 test
vim test_experiment.yml

# Save as new recipe
ece4-exp save --expid test --recipe gcm-sr

# Reuse it
ece4-exp generate my-recipe 10 a001
```

**Scripting support:**
```bash
# Quiet mode (no colors, for scripts)
ece4-exp generate gcm-sr 10 a001 --quiet

# Batch generation
for exp in a001 a002 a003; do
  ece4-exp generate gcm-sr 10 $exp --quiet
done
```

---

# Platform Support

**Currently supported:**
- 🇪🇸 BSC MareNostrum 5
- 🇮🇹 ECMWF HPC2020

**Adding a new platform:**
1. Create `~/.config/ece4-exp/platforms/<name>.yml`
2. Set `ppn` (cores per node) and node layouts per experiment type
3. Done!

**Example (key fields):**
```yaml
ppn: 128                   # Cores per node
slurm-wrapper-taskset:
  CPLD-SR:                 # Coupled GCM layout
    slurm:
      sbatch:
        opts:
          time: "01:00:00"
    groups:
      - {nodes: 1, oifs: 25, nemo: 9, xios: 1, rnfm: 1}
      - {nodes: 9, oifs: 25, nemo: 10, xios: 1}
```

Copy a built-in platform as template and adjust node layouts.

---

# Get Started

**The full workflow:**

```bash
pip install ece4-exp
ece4-exp setup                          # configure once
ece4-exp generate gcm-sr 10 a001        # generate config
ece4-exp deploy a001                    # push to HPC
```

**Then on the HPC:**
```bash
cd $scratch/ecearth4/scripts/runtime
se user.yml platform.yml a001_experiment.yml scriptlib/main.yml
```

**Documentation:**
- `ece4-exp --help` — Command reference
- https://ece4-exp.readthedocs.io

**Compatible with:**
- ✅ Manual EC-Earth4 workflows (ScriptEngine / `se`)
- ✅ Autosubmit (auto-ecearth4) - backward compatible

**Questions?** vladimir.lapin@bsc.es  
**Code:** https://github.com/vlap/ece4-exp
