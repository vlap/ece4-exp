# EC-Earth4 YAML Configuration Tools (ece4-recipe)

Standalone tools for managing EC-Earth4 experiment configurations using a modular YAML overlay system.

## Quick Start

### 1. Installation

```bash
git clone https://github.com/vlap/ece4-recipe.git
cd ece4-recipe
pip install -r requirements.txt
```

### 2. Setup

```bash
./ece4-recipe.sh init-user
```

### 3. Generate

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

## Structure

- ece4-recipe.sh: Main CLI wrapper.
- ece4_recipe/: Core Python implementation.
- recipes/: Collection of YAML recipes.
- configs/: Base configuration fragments.
- platforms/: Platform-specific launcher definitions.
- templates/: Templates for user configuration.
