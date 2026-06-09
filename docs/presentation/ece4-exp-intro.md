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
---

<!-- _class: lead -->

# ece4-exp

## EC-Earth4 Experiment Configuration Made Simple

**From hours of YAML editing to 30 seconds**

---

# The Problem

**Creating an EC-Earth4 experiment config is painful:**

- Edit 257-line YAML file manually
- Match components, grids, and processor counts
- Calculate node layouts and resource distribution
- Set platform paths, SLURM settings, forcing...
- Easy to make mistakes (typos, incompatible combinations)

**Result:** 2-4 hours for experienced users, longer for newcomers

---

# The Solution

**One command generates production-ready configs:**

```bash
./ece4-exp generate \
  --recipe gcm-sr.yml \
  --sim-procs 1120 \
  --expid my-experiment
```

**That's it.** You get:
- Correct component configuration
- Calculated node layout (10 nodes)
- Validated and ready to run

---

# What You Get

**Pre-tested recipes for common experiments:**
- `gcm-sr.yml` - Coupled atmosphere-ocean
- `omip-sr.yml` - Ocean-only with ERA5 forcing
- `amip-sr.yml` - Atmosphere-only
- `ccycle-sr.yml` - With carbon cycle (LPJG)

**Smart features:**
- Auto-calculates processor distribution
- Fetches platform configs from EC-Earth4 repo
- Validates before you submit
- Works on BSC, ECMWF (to add a platform just a file with launcher templates is needed)

---

# Real Example: GCM vs OMIP

**Coupled atmosphere-ocean (10 nodes):**
```bash
./ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120
# OIFS + NEMO + XIOS + OASIS + RNFM
```

**Ocean-only (2 nodes):**
```bash
./ece4-exp generate --recipe omip-sr.yml --sim-procs 224
# NEMO + XIOS (no atmosphere)
```

Different science, different resources - same simple command.

---

# Setup Once, Use Forever

**One-time setup:**
```bash
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
./setup.sh
./ece4-exp init-user
```

**Then just:**
```bash
./ece4-exp generate --recipe <type> --sim-procs <n>
```

Your platform, account, scratch are remembered.
Override when needed: `--platform ecmwf-hpc2020`

---

# Get Started

**Try it now:**

```bash
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
./QUICK_DEMO.sh
```

**Documentation:**
- `README.md` - Complete guide
- `DEMO.md` - Full walkthrough with examples
- `./ece4-exp --help` - Command reference

**Compatible with:** auto-ecearth4 (Autosubmit) and manual workflows

**Questions?** vladimir.lapin@bsc.es
