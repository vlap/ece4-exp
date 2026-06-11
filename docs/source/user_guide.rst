User Guide
==========

This guide covers all |ece4exp| commands and features.

Commands
--------

list
~~~~

List available recipes and their locations.

.. code-block:: bash

   ece4-exp list

**Output:**

* User recipes (from ``~/.config/ece4-exp/recipes/``)
* Built-in recipes (from package installation)
* Directory locations
* Usage tips

inspect
~~~~~~~

View recipe contents and location.

.. code-block:: bash

   ece4-exp inspect <recipe.yml>

**Example:**

.. code-block:: bash

   ece4-exp inspect gcm-sr.yml

Shows full YAML content and physical file path.

generate
~~~~~~~~

Generate experiment configuration.

.. code-block:: bash

   ece4-exp generate --recipe <recipe.yml> --sim-procs <N> --expid <id>

**Required parameters:**

* ``--recipe`` - Recipe file name
* ``--sim-procs`` - Number of processors
* ``--expid`` - 4-character experiment ID

**Optional parameters:**

* ``--platform`` - HPC platform (e.g., bsc-marenostrum5)
* ``--launcher`` - Launch method (e.g., slurm-wrapper-taskset)
* ``--account`` - HPC account/project
* ``--walltime`` - Walltime in hours
* ``--description`` - Experiment description
* ``--repo-owner`` - EC-Earth4 repo owner
* ``--repo-branch`` - EC-Earth4 version/branch
* ``-o, --output`` - Output filename
* ``--dry-run`` - Preview without creating file
* ``--quiet`` - Suppress colored output

**Parameter resolution order:**

1. CLI flags (highest priority)
2. User defaults (``~/.config/ece4-exp/defaults.yml``)
3. Autosubmit files (if using ``--expdef``/``--jobs``)
4. Built-in defaults

**Example:**

.. code-block:: bash

   ece4-exp generate \\
     --recipe gcm-sr.yml \\
     --sim-procs 1120 \\
     --expid a001 \\
     --platform bsc-marenostrum5 \\
     --account bsc32 \\
     --walltime 2  # Override default \\
     --description "Test run"

validate
~~~~~~~~

Validate experiment configuration.

.. code-block:: bash

   ece4-exp validate <config-file>

**Checks:**

* YAML syntax
* Required fields present
* Component configurations
* Schema compliance

**Example:**

.. code-block:: bash

   ece4-exp validate a001_experiment.yml

save
~~~~

Save modifications as a reusable recipe.

.. code-block:: bash

   ece4-exp save --expid <id> --recipe <base-recipe.yml> [-o output.yml]

**Default behavior:**

* Saves to ``~/.config/ece4-exp/recipes/<expid>.yml``
* Use ``-o`` to specify custom location

**Important:** Always specify ``--recipe`` to include the base recipe content.

**Example workflow:**

.. code-block:: bash

   # 1. Generate and modify
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test
   vim test_experiment.yml  # Make changes

   # 2. Save as recipe
   ece4-exp save --expid test --recipe gcm-sr.yml

   # 3. Reuse
   ece4-exp generate --recipe test.yml --sim-procs 1120 --expid prod

setup
~~~~~

Initialize user configuration file.

.. code-block:: bash

   ece4-exp setup

Creates ``~/.config/ece4-exp/defaults.yml`` with template values.

**Edit to set your defaults:**

.. code-block:: yaml

   platform: bsc-marenostrum5
   launcher: slurm-wrapper-taskset
   account: bsc32
   qos: gp_bsces
   repo_owner: ec-earth
   repo_branch: v4.1.8

   # Note: Walltime set automatically per experiment type in platform configs
   #   CPLD-SR: 1h, OMIP-SR: 30min, AMIP-SR: 30min, CCCL-SR: 1.5h

info
~~~~

Show current configuration info (for debugging).

.. code-block:: bash

   ece4-exp info

Configuration System
--------------------

YAML Overlay System
~~~~~~~~~~~~~~~~~~~

Configurations merge in this order:

1. Base config (from EC-Earth4 repo)
2. Platform launcher (from ``platforms/``)
3. Recipe (from ``recipes/`` or user recipes)
4. User defaults (``~/.config/ece4-exp/defaults.yml``)
5. CLI flags

Each layer overrides previous layers.

User Recipes
~~~~~~~~~~~~

Store custom recipes in ``~/.config/ece4-exp/recipes/``:

**Creating user recipes:**

Method 1 - Save modifications:

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test
   # Edit test_experiment.yml
   ece4-exp save --expid test --recipe gcm-sr.yml

Method 2 - Copy existing:

.. code-block:: bash

   cp /path/to/recipe.yml ~/.config/ece4-exp/recipes/

Method 3 - Create from scratch:

.. code-block:: yaml

   # ~/.config/ece4-exp/recipes/my-gcm.yml
   - base.context:
       experiment:
         monitoring:
           activate: true
       model_config:
         components: [oifs, xios, nemo, oasis]
         oifs:
           grid: TL511L91  # High resolution

**Recipe search priority:**

1. User recipes (``~/.config/ece4-exp/recipes/``)
2. Built-in recipes (package installation)
3. Absolute paths

**Sharing recipes:**

.. code-block:: bash

   # Export
   cp ~/.config/ece4-exp/recipes/my-recipe.yml /shared/team/

   # Import
   cp /shared/team/my-recipe.yml ~/.config/ece4-exp/recipes/

Platform Support
----------------

Currently supported platforms:

* BSC MareNostrum 5 (``bsc-marenostrum5``)
* ECMWF HPC2020 (``ecmwf-hpc2020``)

**Customize or add platforms:**

User platforms in ``~/.config/ece4-exp/platforms/`` override built-in platforms.

.. code-block:: bash

   # Copy built-in platform as template
   cp platforms/bsc-marenostrum5.yml ~/.config/ece4-exp/platforms/my-hpc.yml

   # Edit launcher settings (ppn, node layouts, OMP threads)
   vim ~/.config/ece4-exp/platforms/my-hpc.yml

   # Use your platform
   ece4-exp generate --recipe gcm-sr.yml --platform my-hpc.yml --sim-procs 1120

**Platform search order:**

1. User platforms (``~/.config/ece4-exp/platforms/``)
2. Built-in platforms (from package)

**Platform file structure:**

Contains launcher configurations for different experiment types:

* ``ppn`` - Processors per node
* ``omp_num_threads`` - OpenMP threads per process
* ``groups`` - Node layout definitions per launcher kind (CPLD-SR, OMIP-SR, etc.)

Autosubmit Integration
----------------------

|ece4exp| can integrate with Autosubmit experiment directories:

.. code-block:: bash

   ece4-exp generate \\
     --recipe gcm-sr.yml \\
     --expdef /path/to/expdef_a001.yml \\
     --jobs /path/to/jobs_a001.yml

This reads defaults from Autosubmit configuration files.

Troubleshooting
---------------

**Missing required parameters error:**

Set user defaults or provide via CLI:

.. code-block:: bash

   ece4-exp setup
   # Or
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001 \\
     --platform bsc-marenostrum5 --account bsc32

**Invalid expid error:**

Expid must be exactly 4 alphanumeric characters:

* Valid: ``a001``, ``test``, ``exp1``
* Invalid: ``a1``, ``experiment``, ``exp-1``

**Recipe not found:**

Check available recipes:

.. code-block:: bash

   ece4-exp list

Verify recipe is in user recipes or built-in recipes.

**Git clone fails:**

Check network connection and repository settings. The tool clones EC-Earth4 config from:

.. code-block:: text

   https://git.smhi.se/<repo-owner>/ecearth4.git

Tips and Best Practices
------------------------

1. **Set up user defaults early** - Saves typing common parameters

2. **Use descriptive expids** - Makes experiments easier to identify

3. **Validate after generate** - Catches errors before submission

4. **Save custom recipes** - Reuse successful configurations

5. **Use --dry-run for testing** - Preview configs before creating files

6. **Keep user recipes organized** - Use clear naming conventions

7. **Share recipes with team** - Standardize experiment setups

8. **Version control your recipes** - Track changes to custom configs

Advanced Usage
--------------

**Generate multiple experiments:**

.. code-block:: bash

   for year in {2000..2010}; do
     ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \\
       --expid y${year:2:2}a --description "Year $year"
   done

**Scripted config generation:**

.. code-block:: bash

   #!/bin/bash
   # gen-experiments.sh

   RECIPE="gcm-sr.yml"
   PROCS=1120
   PLATFORM="bsc-marenostrum5"
   ACCOUNT="bsc32"

   for exp in exp1 exp2 exp3; do
     ece4-exp generate --recipe $RECIPE --sim-procs $PROCS \\
       --expid $exp --platform $PLATFORM --account $ACCOUNT
   done

**Custom processor distributions:**

Different experiments need different processor counts:

* GCM SR: 1120 (10 nodes × 112 cores)
* OMIP SR: 224 (2 nodes × 112 cores)
* AMIP SR: 896 (8 nodes × 112 cores)

Calculate based on your platform's cores per node.

For full details, see the complete guide: ``docs/GUIDE.md`` in the repository.
