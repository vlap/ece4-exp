---
marp: true
paginate: true
theme: gaia
backgroundColor: '#f5f5f5'
color: '#333'
header: 'ece4-recipe: Standalone EC-Earth4 YAML Tools'
footer: 'Vladimir Lapin (BSC) | 2026'
---

# `ece4-recipe`
### Effortless EC-Earth4 Configuration Management

A standalone toolkit for reproducible climate experiment setups.

---

# The Problem: Configuration Hell

- **Complexity**: EC-Earth4 YAMLs are powerful but complex.
- **Fragmentation**: Duplicate configs across experiments.
- **Dependency**: Hard to test or generate configs outside of a heavy workflow manager.
- **Traceability**: Hard to know "exactly" what went into a configuration.

---

# The Solution: `ece4-recipe`

**A Modular, Standalone Tool**

- **Decoupled**: Works anywhere (Local, MN5, ECMWF).
- **Stitched**: Uses a "Merge Model" to layer configurations.
- **Versioned**: Automatically syncs with specific EC-Earth4 source tags.
- **Reproducible**: Save your modifications as a minimal "Recipe".

---

# How it Works: The Merge Model

Configurations are layered like a cake:

1. **[BASE]** experiment-config-example.yml (from ECE4 repo)
2. **[PLATFORM]** Slurm/HPC settings (MN5, HPC2020, etc.)
3. **[RECIPE]** Your scientific setup (gcm-sr.yml, omip-hr.yml)
4. **[OVERRIDE]** Your specific experiment tweaks.

---

# Demo: Instant Configuration

No dummy files needed. Just one command:

```bash
./ece4-recipe.sh generate --dry-run \
  --repo-owner ec-earth \
  --repo-branch v4.1.6 \
  --platform bsc-marenostrum5 \
  --sim-procs 1120 \
  --kind auto \
  --launcher slurm-wrapper-taskset \
  --recipe gcm-sr.yml
```

**Result**: A fully verified, 10-node Slurm configuration ready to go.

---

# Key Features for Researchers

- **Quick Validation**: Catch syntax or schema errors instantly.
- **Recipe Sharing**: Save your custom setup as a tiny YAML fragment.
- **HPC Ready**: Pre-configured for BSC and ECMWF.
- **Bash Completion**: High developer ergonomics.

---

# Sharing Science: Save your Recipe

Modified your experiment and found a perfect setup?

```bash
# Saves only your changes relative to the base
./ece4-recipe.sh save my-breakthrough-setup.yml
```

**Result**: A clean, shareable recipe that anyone can use to reproduce your experiment exactly.

---

# Get Started Today

**Github**: https://github.com/vlap/ece4-recipe

```bash
git clone https://github.com/vlap/ece4-recipe.git
./ece4-recipe.sh init-user
./ece4-recipe.sh list
```

**Questions?**
vladimir.lapin@bsc.es
