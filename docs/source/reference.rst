Reference
=========

Complete command reference with use cases and examples.

Commands Overview
-----------------

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Command
     - Purpose
     - Use Case
   * - **setup**
     - Configure platform and account
     - First-time setup or changing HPC system
   * - **list**
     - Show available recipes
     - Discover what experiments you can generate
   * - **generate**
     - Create experiment config
     - Main command — generate ready-to-run configs
   * - **inspect**
     - View recipe contents
     - Understand what a recipe configures
   * - **save**
     - Save modifications as recipe
     - Reuse customizations across experiments
   * - **validate**
     - Check config validity
     - Debug configuration issues
   * - **completion**
     - Generate shell completion script
     - Enable TAB completion manually

setup
-----

**Purpose**: Configure platform, account, and defaults

**Use case**: Run once when you first install, or when switching HPC platforms.

.. code-block:: bash

   ece4-exp setup

Asks 4 questions:

1. Platform (MareNostrum5 or ECMWF HPC2020)
2. Account/project name
3. QoS (quality of service)
4. Username (optional, for reference)

Creates ``~/.config/ece4-exp/defaults.yml``. Also shows the TAB completion command to add to your shell config.

**When to re-run**:

* Switching HPC platforms
* Changing to a different account/project
* After deleting ``~/.config/ece4-exp/``

**Example interaction**:

.. code-block:: text

   ece4-exp Interactive Setup

   1. Which HPC platform do you use?
      [1] BSC MareNostrum 5
      [2] ECMWF HPC2020
   Enter 1 or 2: 1

   2. What is your project/account name?
      (e.g., bsc32)
   Account [bsc32]: bsc32

   3. QoS (Quality of Service)?
      Default for bsc-marenostrum5: gp_bsces
   QoS [gp_bsces]:

   4. Your username (optional, for reference)?
      (e.g., bsc32XXX)
   Username [skip]:

   ✓ Configuration saved to: ~/.config/ece4-exp/defaults.yml

list
----

**Purpose**: Show available recipes and their locations

**Use case**: Discover what experiments you can generate, check if your custom recipes are recognized.

.. code-block:: bash

   ece4-exp list

**Example output**:

.. code-block:: text

   Available Recipes:

   Your Recipes:
     - my-custom.yml

   Built-in Recipes:
     - gcm-sr.yml
     - omip-sr.yml
     - amip-sr.yml
     - ccycle-sr.yml
     - aa2s.yml
     - OMIP_with_ERA5_6_Cycles.yml

   Locations:
     User recipes:     ~/.config/ece4-exp/recipes (1 custom)
     Built-in recipes: /path/to/site-packages/ece4_exp/recipes
     User platforms:   ~/.config/ece4-exp/platforms (empty)
     Built-in platforms: /path/to/site-packages/ece4_exp/platforms

**When to use**:

* Forgot recipe names
* Checking if a custom recipe is in the right place
* Verifying package installation

generate
--------

**Purpose**: Generate experiment configuration file

**Use case**: The main command. Takes a recipe, number of nodes, and experiment ID; produces a ready-to-submit YAML config.

**Syntax**:

.. code-block:: bash

   ece4-exp generate RECIPE NODES EXPID [OPTIONS]

**Arguments**:

* ``RECIPE`` — Recipe name (with or without ``.yml``, e.g. ``gcm-sr`` or ``gcm-sr.yml``)
* ``NODES`` — Number of compute nodes
* ``EXPID`` — 4-character alphanumeric experiment ID (EC-Earth4 standard)

**Common options**:

* ``--walltime HOURS`` — Walltime in hours (overrides platform default)
* ``--platform PLATFORM`` — Override default platform
* ``--account ACCOUNT`` — Override default account
* ``-o FILE`` — Custom output filename (default: ``{expid}_experiment.yml``)
* ``--dry-run`` — Print generated YAML without writing to file
* ``--quiet`` — No colors, for scripting

**Node-to-processor conversion**:

The tool multiplies your node count by the platform's cores-per-node:

* MareNostrum5: 112 cores/node → ``10 nodes = 1120 cores``
* ECMWF HPC2020: 128 cores/node → ``10 nodes = 1280 cores``

**Basic examples**:

.. code-block:: bash

   # Coupled GCM, 10 nodes
   ece4-exp generate gcm-sr 10 a001
   # → Creates: a001_experiment.yml

   # Ocean-only, 2 nodes
   ece4-exp generate omip-sr 2 o001

   # Atmosphere-only, 8 nodes with custom walltime
   ece4-exp generate amip-sr 8 atm1 --walltime 72

**With options**:

.. code-block:: bash

   # Generate for ECMWF (overrides platform from defaults.yml)
   ece4-exp generate gcm-sr 10 a001 --platform ecmwf-hpc2020

   # Preview config without writing
   ece4-exp generate gcm-sr 10 a001 --dry-run

   # Quiet output (no colors), useful in scripts
   ece4-exp generate gcm-sr 10 a001 --quiet

**Ensemble / batch generation**:

.. code-block:: bash

   # 5-member ensemble (4-char IDs: e001..e005)
   for i in 001 002 003 004 005; do
     ece4-exp generate gcm-sr 10 e${i} --walltime 48
   done

   # Sweep over experiment types
   ece4-exp generate gcm-sr  10 gcm1   # Coupled
   ece4-exp generate omip-sr  4 ocn1   # Ocean-only
   ece4-exp generate amip-sr  8 atm1   # Atmosphere-only

**Backward compatibility** (original ``--sim-procs`` style still works):

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

**Error handling**:

.. code-block:: bash

   # Invalid expid (too long):
   ece4-exp generate gcm-sr 10 toolong
   # ERROR: Invalid expid 'toolong': Must be exactly 4 alphanumeric characters
   # Examples: a001, test, exp1, gcm4

   # Missing arguments:
   ece4-exp generate gcm-sr
   # ERROR: Missing required arguments: NODES, EXPID
   # Usage: ece4-exp generate RECIPE NODES EXPID

inspect
-------

**Purpose**: View recipe contents and location

**Use case**: Understand what a recipe configures before using it, or find where it lives so you can copy/edit it.

.. code-block:: bash

   ece4-exp inspect RECIPE

**Examples**:

.. code-block:: bash

   ece4-exp inspect gcm-sr          # .yml extension optional
   ece4-exp inspect gcm-sr.yml      # same result
   ece4-exp inspect my-custom       # works for user recipes too

**Example output**:

.. code-block:: text

   Recipe: gcm-sr.yml
   Location: /path/to/ece4_exp/recipes/gcm-sr.yml

   - base.context:
       experiment:
         monitoring:
           activate: true
       model_config:
         components: [oifs, nemo, xios, rnfm, oasis]
         oifs:
           grid: TL255L91
           precision: DP
         nemo:
           grid: eORCA1L75_ISO

Recipes are YAML overlays — they contain only the fields that differ from the base config. The ``- base.context:`` block is the EC-Earth4 ScriptEngine format for context injection.

save
----

**Purpose**: Save your modifications to a generated config as a reusable recipe

**Use case**: You generated a config, edited it (changed grid resolution, enabled extra output, tweaked model settings), and want to reuse those changes for future experiments.

**Workflow**:

.. code-block:: bash

   # 1. Generate
   ece4-exp generate gcm-sr 10 test

   # 2. Edit the config
   vim test_experiment.yml

   # 3. Save as recipe
   ece4-exp save --expid test --recipe gcm-sr

   # 4. Reuse in future experiments
   ece4-exp generate test 10 prod

**How it works**:

Compares your edited ``test_experiment.yml`` against the pristine copy saved at generation time (``~/.config/ece4-exp/test_experiment_pristine.yml``) and extracts only the differences. These become the new recipe overlay, so it stays compact.

**Arguments**:

* ``--expid EXPID`` — Experiment ID (required, 4 alphanumeric characters)
* ``--config FILE`` — Path to the edited experiment YAML (default: ``{expid}_experiment.yml`` in CWD)
* ``--recipe BASE`` — Base recipe name to build on
* ``-o OUTPUT`` — Output recipe path (default: ``~/.config/ece4-exp/recipes/{expid}.yml``)

**Real-world examples**:

.. code-block:: bash

   # High-resolution variant
   ece4-exp generate gcm-sr 20 hihr
   vim hihr_experiment.yml      # Change oifs.grid to TL511L91
   ece4-exp save --expid hihr --recipe gcm-sr
   # Now use: ece4-exp generate hihr 20 a001

   # Team-shared config
   ece4-exp generate gcm-sr 10 team
   vim team_experiment.yml      # Add team-specific output variables
   ece4-exp save --expid team --recipe gcm-sr -o /shared/recipes/team.yml

**Important**: Always specify ``--recipe`` to include the base recipe content in the saved file.

validate
--------

**Purpose**: Check configuration file validity

**Use case**: Debug configuration issues, or verify a config you manually edited.

.. code-block:: bash

   ece4-exp validate CONFIG_FILE

**Examples**:

.. code-block:: bash

   ece4-exp validate a001_experiment.yml

   # Typical after manual editing:
   vim a001_experiment.yml
   ece4-exp validate a001_experiment.yml

**Example output**:

.. code-block:: text

   ✓ Valid YAML syntax
   ✓ Required fields present
   ✓ Component configuration valid
   ✓ Configuration is valid

**Note**: Validation runs automatically during ``generate``, so this command is mainly useful after manual edits.

completion
----------

**Purpose**: Enable TAB completion for commands, recipe names, and flags.

**Setup** (one-time, add to your shell config file):

.. code-block:: bash

   # bash — add to ~/.bashrc:
   eval "$(register-python-argcomplete ece4-exp)"

   # zsh — add to ~/.zshrc:
   eval "$(register-python-argcomplete ece4-exp)"

Then run ``source ~/.bashrc`` (or ``~/.zshrc``), or restart your shell.

**What it enables**:

.. code-block:: bash

   ece4-exp ge<TAB>              # → ece4-exp generate
   ece4-exp generate gc<TAB>    # → ece4-exp generate gcm-sr
   ece4-exp generate gcm-sr 10 a001 --w<TAB>  # → --walltime

**Manual script generation** (if automatic setup doesn't work):

.. code-block:: bash

   # Generate and source directly:
   eval "$(ece4-exp completion bash)"   # bash
   eval "$(ece4-exp completion zsh)"    # zsh

Configuration Files
-------------------

User Defaults (``~/.config/ece4-exp/defaults.yml``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Created by ``ece4-exp setup``. All fields are optional — you only need the ones you want to pre-fill.

.. code-block:: yaml

   # Platform & EC-Earth4 Version
   platform: bsc-marenostrum5
   launcher: slurm-wrapper-taskset  # Rarely needs changing
   kind: auto                       # Auto-detects from recipe

   repo_owner: ec-earth             # Official EC-Earth4 repo
   repo_branch: v4.1.8              # Pinned stable version

   # Your HPC Account
   account: bsc32
   qos: gp_bsces

   # Optional: Pre-fill recipe and/or node count to save typing
   # recipe: gcm-sr
   # sim_procs: 1120

**Resolution order**: CLI flags > ``defaults.yml`` > Platform defaults

User Recipes (``~/.config/ece4-exp/recipes/``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom recipes stored here override built-in recipes with the same name.

**Creating recipes — three methods**:

*Method 1* — Save from a generated experiment (recommended):

.. code-block:: bash

   ece4-exp generate gcm-sr 10 test
   vim test_experiment.yml           # Make your changes
   ece4-exp save --expid test --recipe gcm-sr

*Method 2* — Copy and modify an existing recipe:

.. code-block:: bash

   cp $(python3 -c "from ece4_exp import paths; print(paths.RECIPES_DIR)")/gcm-sr.yml \
      ~/.config/ece4-exp/recipes/my-gcm.yml
   vim ~/.config/ece4-exp/recipes/my-gcm.yml

*Method 3* — Write from scratch (advanced):

.. code-block:: yaml

   # ~/.config/ece4-exp/recipes/hi-res.yml
   - base.context:
       model_config:
         oifs:
           grid: TL511L91     # High-resolution atmosphere
         nemo:
           grid: eORCA025L75  # High-resolution ocean

Recipes use the EC-Earth4 ScriptEngine ``base.context`` format. Only specify fields that differ from the base config.

**Sharing recipes with colleagues**:

.. code-block:: bash

   # Share
   cp ~/.config/ece4-exp/recipes/my-recipe.yml /shared/team/

   # Use a shared recipe
   cp /shared/team/my-recipe.yml ~/.config/ece4-exp/recipes/
   ece4-exp generate my-recipe 10 a001

User Platforms (``~/.config/ece4-exp/platforms/``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom platform launcher files stored here override built-in platforms with the same name.

.. code-block:: bash

   # Copy built-in platform as a starting template
   cp $(python3 -c "from ece4_exp import paths; print(paths.PLATFORMS_DIR)")/bsc-marenostrum5.yml \
      ~/.config/ece4-exp/platforms/my-hpc.yml

   vim ~/.config/ece4-exp/platforms/my-hpc.yml
   ece4-exp generate gcm-sr 10 a001 --platform my-hpc

**Platform file structure** (key fields):

.. code-block:: yaml

   ppn: 112                # Processors per node — used to convert nodes → procs

   slurm-wrapper-taskset:  # Launcher type (matching --launcher)
     CPLD-SR:              # Launcher kind (auto-detected from recipe)
       slurm:
         sbatch:
           opts:
             time: "01:00:00"
       groups:             # Node layout: how cores are divided among components
         - {nodes: 1, oifs: 25, nemo: 9, xios: 1, rnfm: 1}
         - {nodes: 9, oifs: 25, nemo: 10, xios: 1}

The ``groups`` list defines how nodes are split between model components. Each entry covers some nodes; ``oifs``, ``nemo``, ``xios``, ``rnfm`` values are the number of MPI tasks for each component on those nodes.

Common Workflows
----------------

**Ensemble generation**:

.. code-block:: bash

   # 5-member ensemble
   for i in 001 002 003 004 005; do
     ece4-exp generate gcm-sr 10 e${i} --walltime 48
   done

**Sensitivity studies**:

.. code-block:: bash

   # Same recipe, different platforms
   ece4-exp generate gcm-sr 10 mn01 --platform bsc-marenostrum5
   ece4-exp generate gcm-sr 10 ec01 --platform ecmwf-hpc2020

   # Different experiment types
   ece4-exp generate gcm-sr  10 gcm1   # Coupled
   ece4-exp generate omip-sr  4 ocn1   # Ocean-only
   ece4-exp generate amip-sr  8 atm1   # Atmosphere-only

**Scripted generation**:

.. code-block:: bash

   #!/bin/bash
   PLATFORM="bsc-marenostrum5"
   ACCOUNT="bsc32"

   for exp in a001 a002 a003; do
     ece4-exp generate gcm-sr 10 $exp \
       --platform $PLATFORM --account $ACCOUNT --quiet
   done

**Custom recipe workflow**:

.. code-block:: bash

   # Create a high-resolution recipe
   ece4-exp generate gcm-sr 40 hihr
   vim hihr_experiment.yml             # Change to TL511L91 + eORCA025L75
   ece4-exp save --expid hihr --recipe gcm-sr

   # Use it from now on
   ece4-exp generate hihr 40 h001

Autosubmit Integration
-----------------------

If you use Autosubmit to manage your experiments, ece4-exp can read parameters from Autosubmit configuration files:

.. code-block:: bash

   ece4-exp generate \
     --recipe gcm-sr.yml \
     --expdef /path/to/autosubmit/a001/conf/expdef_a001.yml \
     --jobs   /path/to/autosubmit/a001/conf/jobs_a001.yml

Parameters in Autosubmit files (platform, account, etc.) are used as a fallback when not specified on the CLI or in ``defaults.yml``.

Troubleshooting
---------------

**"ERROR: Missing required arguments"**

Run ``ece4-exp setup`` to configure your platform and account defaults.

**"ERROR: Invalid expid"**

The experiment ID must be exactly 4 alphanumeric characters:

* Valid: ``a001``, ``test``, ``exp1``, ``ctrl``
* Invalid: ``a1``, ``experiment``, ``exp-1``, ``test1234``

**"ERROR: Recipe not found"**

.. code-block:: bash

   ece4-exp list    # Check available recipe names

**"ERROR: Pristine file not found"** (when using ``save``)

You must ``generate`` the experiment first before you can ``save`` modifications. The pristine copy is created at generation time.

**TAB completion not working**

Make sure you have added the eval line to your shell config:

.. code-block:: bash

   echo 'eval "$(register-python-argcomplete ece4-exp)"' >> ~/.bashrc
   source ~/.bashrc

**Git clone fails** (no network access or private repo)

The tool fetches base config from ``https://git.smhi.se/ec-earth/ecearth4.git``.
Check network access, or use ``--repo-owner`` to point to a mirror.

**Recipe changes not taking effect**

User recipes take priority over built-in ones. Run ``ece4-exp list`` to verify which file is being found.

Exit Codes
----------

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Code
     - Meaning
   * - 0
     - Success
   * - 1
     - Error (missing args, invalid input, file not found)
   * - 130
     - Interrupted by user (Ctrl+C)

Debug Mode
----------

.. code-block:: bash

   # Enable full stack traces on errors:
   DEBUG=1 ece4-exp generate gcm-sr 10 a001

Python API
----------

For programmatic use in scripts or notebooks:

.. code-block:: python

   import sys
   from ece4_exp import cli

   # Run a command
   sys.argv = ['ece4-exp', 'generate', 'gcm-sr', '10', 'a001']
   cli.main()

   # Access paths
   from ece4_exp import paths
   print(paths.RECIPES_DIR)        # Built-in recipes directory
   print(paths.USER_DEFAULTS_FILE) # User defaults file

   # Load and merge YAML configs
   from ece4_exp.yaml_util import load_yaml_config, deep_merge
   base   = load_yaml_config('base.yml')
   recipe = load_yaml_config('gcm-sr.yml')
   merged = deep_merge(base, recipe)

See full source at: https://github.com/vlap/ece4-exp
