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
     - Main command - generate ready-to-run configs
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
     - Generate shell completion
     - Enable TAB completion

setup
-----

**Purpose**: Configure platform, account, and defaults

**Use case**: Run once when you first install, or when switching HPC platforms.

**Interactive setup**:

.. code-block:: bash

   ece4-exp setup

Asks 4 questions:
1. Platform (MareNostrum5 or ECMWF HPC2020)
2. Account/project name
3. QoS (quality of service)
4. Username (optional, for reference)

Creates ``~/.config/ece4-exp/defaults.yml``.

**When to re-run**:
- Switching HPC platforms
- Changing to a different account/project
- After deleting ``~/.config/ece4-exp/``

**Example output**:

.. code-block:: text

   ece4-exp Interactive Setup
   ========================================

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

**Basic usage**:

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
- Forgot recipe names
- Checking if custom recipe is in the right place
- Verifying package installation

generate
--------

**Purpose**: Generate experiment configuration file

**Use case**: Main command for creating ready-to-run EC-Earth4 configs.

**Syntax**:

.. code-block:: bash

   ece4-exp generate RECIPE NODES EXPID [OPTIONS]

**Arguments**:

* ``RECIPE`` - Recipe name (with or without ``.yml``)
* ``NODES`` - Number of compute nodes
* ``EXPID`` - 4-character experiment ID (alphanumeric)

**Common options**:

* ``--walltime HOURS`` - Walltime in hours
* ``--platform PLATFORM`` - Override default platform
* ``--account ACCOUNT`` - Override default account
* ``-o FILE`` - Custom output filename
* ``--dry-run`` - Preview without writing

**Examples**:

**Basic generation**:

.. code-block:: bash

   # Coupled GCM, 10 nodes, ID=a001
   ece4-exp generate gcm-sr 10 a001
   # → Creates: a001_experiment.yml

   # Ocean-only, 2 nodes
   ece4-exp generate omip-sr 2 o001

   # Atmosphere-only, 8 nodes
   ece4-exp generate amip-sr 8 atm1

**With options**:

.. code-block:: bash

   # Custom walltime (72 hours)
   ece4-exp generate gcm-sr 10 a002 --walltime 72

   # Different platform
   ece4-exp generate gcm-sr 10 a003 --platform ecmwf-hpc2020

   # Custom output filename
   ece4-exp generate gcm-sr 10 a004 -o my-config.yml

   # Preview without writing
   ece4-exp generate gcm-sr 10 a005 --dry-run

**Node calculation**:

The tool automatically calculates processors:

* MareNostrum5: 112 cores/node → 10 nodes = 1120 cores
* ECMWF HPC2020: 128 cores/node → 10 nodes = 1280 cores

**Backward compatibility** (old style):

.. code-block:: bash

   # Still works: specify processors directly
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

**Common use cases**:

.. code-block:: bash

   # 1. Quick test (2 nodes)
   ece4-exp generate gcm-sr 2 test

   # 2. Production run (20 nodes, 48h walltime)
   ece4-exp generate gcm-sr 20 prod --walltime 48

   # 3. Ensemble members (10 configs)
   for i in {01..10}; do
     ece4-exp generate gcm-sr 10 e$i --walltime 24
   done

   # 4. Different experiment types
   ece4-exp generate gcm-sr 10 coupled   # Coupled
   ece4-exp generate omip-sr 4 ocean     # Ocean-only
   ece4-exp generate amip-sr 8 atmos     # Atmosphere-only

**Error handling**:

Invalid expid:

.. code-block:: bash

   ece4-exp generate gcm-sr 10 toolong
   # ERROR: Invalid expid 'toolong': Must be exactly 4 alphanumeric characters
   # Examples: a001, test, exp1, gcm4

Missing arguments:

.. code-block:: bash

   ece4-exp generate gcm-sr
   # ERROR: Missing required arguments: NODES, EXPID
   #
   # Usage:
   #   ece4-exp generate RECIPE NODES EXPID

inspect
-------

**Purpose**: View recipe contents and location

**Use case**: Understand what a recipe configures before using it, find where a recipe is located.

**Syntax**:

.. code-block:: bash

   ece4-exp inspect RECIPE

**Examples**:

.. code-block:: bash

   # View built-in recipe
   ece4-exp inspect gcm-sr

   # View user recipe
   ece4-exp inspect my-custom

   # .yml extension optional
   ece4-exp inspect gcm-sr.yml  # Same as above

**Example output**:

.. code-block:: text

   Recipe: gcm-sr.yml
   Location: /path/to/ece4_exp/recipes/gcm-sr.yml

   ─────────────────────────────────────────
   - base.context:
       experiment:
         monitoring:
           activate: true
       model_config:
         components: ['oifs', 'nemo', 'xios', 'oasis']
         oifs:
           grid: "TL255L91"
           precision: "DP"
         nemo:
           grid: "eORCA1L75_ISO"
   ─────────────────────────────────────────

**When to use**:

* Before using a new recipe
* Comparing recipes
* Finding the path to edit a recipe
* Understanding recipe structure

save
----

**Purpose**: Save modifications as a reusable recipe

**Use case**: You generated a config, edited it, and want to reuse those changes.

**Workflow**:

.. code-block:: bash

   # 1. Generate experiment
   ece4-exp generate gcm-sr 10 test

   # 2. Edit the config
   vim test_experiment.yml
   # Make changes (e.g., change grid resolution, add variables)

   # 3. Save as recipe
   ece4-exp save --expid test --recipe gcm-sr

   # 4. Reuse your recipe
   ece4-exp generate test 10 prod

**How it works**:

Compares your edited file (``test_experiment.yml``) against the pristine copy (``~/.config/ece4-exp/test_experiment_pristine.yml``) and saves only the differences to ``~/.config/ece4-exp/recipes/test.yml``.

**Arguments**:

* ``--expid EXPID`` - Experiment ID (must match the generated config)
* ``--recipe BASE`` - Base recipe name (to include its content)
* ``-o OUTPUT`` - Custom output location (optional)

**Examples**:

.. code-block:: bash

   # Save to user recipes (default)
   ece4-exp save --expid test --recipe gcm-sr
   # → Saves to: ~/.config/ece4-exp/recipes/test.yml

   # Custom output location
   ece4-exp save --expid test --recipe gcm-sr -o /shared/team/my-recipe.yml

**Common use cases**:

.. code-block:: bash

   # 1. High-resolution variant
   ece4-exp generate gcm-sr 20 hihr
   vim hihr_experiment.yml  # Change to TL511L91
   ece4-exp save --expid hihr --recipe gcm-sr
   # Now: ece4-exp generate hihr 20 a001

   # 2. Custom monitoring setup
   ece4-exp generate gcm-sr 10 mon1
   vim mon1_experiment.yml  # Add custom output variables
   ece4-exp save --expid mon1 --recipe gcm-sr

   # 3. Team-specific config
   ece4-exp generate gcm-sr 10 team
   vim team_experiment.yml  # Team-specific settings
   ece4-exp save --expid team --recipe gcm-sr
   cp ~/.config/ece4-exp/recipes/team.yml /shared/recipes/

**Important**: Always specify ``--recipe`` to include the base recipe content.

validate
--------

**Purpose**: Check configuration file validity

**Use case**: Debug configuration issues, verify config before submission.

**Syntax**:

.. code-block:: bash

   ece4-exp validate CONFIG_FILE

**Examples**:

.. code-block:: bash

   # Validate generated config
   ece4-exp validate a001_experiment.yml

   # Validate after manual editing
   vim a001_experiment.yml
   ece4-exp validate a001_experiment.yml

**Example output**:

.. code-block:: text

   ✓ Valid YAML syntax
   ✓ Required fields present
   ✓ Component configuration valid
   ✓ Configuration is valid

**When to use**:

* After manually editing a config
* Debugging generation issues
* Before submitting experiment to EC-Earth4
* Automated testing in scripts

**Note**: Validation happens automatically during ``generate``, so this command is mainly for manual debugging.

completion
----------

**Purpose**: Generate shell completion script

**Use case**: Enable TAB completion for recipe names, commands, and options.

**Syntax**:

.. code-block:: bash

   ece4-exp completion {bash|zsh}

**Setup**:

.. code-block:: bash

   # One-time setup - no config file editing needed
   activate-global-python-argcomplete --user
   # Restart your shell

That's it! This enables completion for ALL Python CLIs (pip, aws, django-admin, ece4-exp, etc.)

**How it works**: Creates ``~/.bash_completion.d/python-argcomplete`` which your shell auto-loads.

**What it enables**:

.. code-block:: bash

   # Command completion
   ece4-exp ge<TAB>     → ece4-exp generate

   # Recipe completion
   ece4-exp generate gc<TAB>  → ece4-exp generate gcm-sr

   # Flag completion
   ece4-exp generate gcm-sr 10 a001 --w<TAB>  → --walltime

**When to use**:

* After installing ece4-exp
* When working frequently with the tool

Common Workflows
----------------

**Ensemble generation**:

.. code-block:: bash

   # 10-member ensemble
   for i in {01..10}; do
     ece4-exp generate gcm-sr 10 e${i} --walltime 48
   done

**Sensitivity studies**:

.. code-block:: bash

   # Different resolutions
   ece4-exp generate gcm-sr 10 sr01    # Standard resolution
   ece4-exp generate gcm-hr 40 hr01    # High resolution (custom recipe)

   # Different forcings
   ece4-exp generate gcm-sr 10 ctrl    # Control
   ece4-exp generate omip-sr 4 ocn1    # Ocean-only

**Team collaboration**:

.. code-block:: bash

   # Create team recipe
   ece4-exp generate gcm-sr 10 team
   vim team_experiment.yml  # Add team settings
   ece4-exp save --expid team --recipe gcm-sr

   # Share with team
   cp ~/.config/ece4-exp/recipes/team.yml /shared/team/

   # Team members use it
   cp /shared/team/team.yml ~/.config/ece4-exp/recipes/
   ece4-exp generate team 10 a001

**Platform migration**:

.. code-block:: bash

   # Generate for MareNostrum5
   ece4-exp generate gcm-sr 10 mn01 --platform bsc-marenostrum5

   # Generate for ECMWF (same recipe, different platform)
   ece4-exp generate gcm-sr 10 ec01 --platform ecmwf-hpc2020

Configuration Files
-------------------

User Defaults
~~~~~~~~~~~~~

Location: ``~/.config/ece4-exp/defaults.yml``

.. code-block:: yaml

   # Platform & EC-Earth4 Version
   platform: bsc-marenostrum5
   launcher: slurm-wrapper-taskset
   kind: auto
   repo_owner: ec-earth
   repo_branch: v4.1.8

   # Your HPC Account
   account: bsc32
   qos: gp_bsces

   # Optional: Auto-fill recipe
   # recipe: gcm-sr

**Resolution order**: CLI flags > User defaults > Platform defaults

User Recipes
~~~~~~~~~~~~

Location: ``~/.config/ece4-exp/recipes/``

Recipe files are YAML overlays that merge with base configurations:

.. code-block:: yaml

   - base.context:
       experiment:
         monitoring:
           activate: true
       model_config:
         components: [oifs, nemo, xios, oasis]
         oifs:
           grid: TL255L91

User Platforms
~~~~~~~~~~~~~~

Location: ``~/.config/ece4-exp/platforms/``

Custom platform configurations:

.. code-block:: bash

   # Copy built-in platform as template
   cp $(python3 -c "from ece4_exp import paths; print(paths.PLATFORMS_DIR)")/bsc-marenostrum5.yml \\
      ~/.config/ece4-exp/platforms/my-hpc.yml

   # Edit for your HPC
   vim ~/.config/ece4-exp/platforms/my-hpc.yml

Troubleshooting
---------------

**"ERROR: Missing required arguments"**:

Run ``ece4-exp setup`` first to configure defaults.

**"ERROR: Invalid expid"**:

Expid must be exactly 4 alphanumeric characters: ``a001``, ``test``, ``exp1`` (not ``a1``, ``experiment``, or ``exp-1``).

**"ERROR: Recipe not found"**:

.. code-block:: bash

   ece4-exp list  # Check available recipes

**"ERROR: Pristine file not found"** (when using ``save``):

You must ``generate`` the experiment first before you can ``save`` modifications.

**Recipe in wrong location**:

User recipes must be in: ``~/.config/ece4-exp/recipes/``

.. code-block:: bash

   # Copy to correct location
   cp my-recipe.yml ~/.config/ece4-exp/recipes/

**Platform not configured**:

.. code-block:: bash

   ece4-exp setup  # Re-run setup

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

Environment Variables
---------------------

* ``CONF_PATH`` - Path to Autosubmit conf directory (for backward compat)
* ``COLOR_NC``, ``COLOR_*`` - Override color output

Debug Mode
----------

.. code-block:: bash

   # Enable debug output
   DEBUG=1 ece4-exp generate gcm-sr 10 a001

   # Or with --debug flag (shows full stack traces)
   ece4-exp generate gcm-sr 10 a001 --debug

Python API
----------

For programmatic use:

.. code-block:: python

   import sys
   from ece4_exp import cli

   # Run command
   sys.argv = ['ece4-exp', 'generate', 'gcm-sr', '10', 'a001']
   cli.main()

   # Load paths
   from ece4_exp import paths
   print(paths.RECIPES_DIR)
   print(paths.USER_DEFAULTS_FILE)

   # Load YAML
   from ece4_exp.yaml_util import load_yaml_config
   config = load_yaml_config('config.yml')

See full API documentation in source code: https://github.com/vlap/ece4-exp
