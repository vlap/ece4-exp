Quick Start
===========

Get started with |ece4exp| in 5 minutes.

30-Second Example
-----------------

Generate a coupled GCM experiment configuration:

.. code-block:: bash

   # Install
   pip install ece4-exp

   # Generate
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

That's it! You now have a complete ``a001_experiment.yml`` configuration file.

Step-by-Step Tutorial
----------------------

1. List Available Recipes
~~~~~~~~~~~~~~~~~~~~~~~~~~

See what experiment types are available:

.. code-block:: bash

   ece4-exp list

Output:

.. code-block:: text

   Available Recipes:

   Built-in Recipes:
     - gcm-sr.yml
     - omip-sr.yml
     - amip-sr.yml
     - ccycle-sr.yml

   Locations:
     User recipes:     ~/.config/ece4-exp/recipes
     Built-in recipes: /path/to/site-packages/recipes

2. Inspect a Recipe
~~~~~~~~~~~~~~~~~~~

View what a recipe configures:

.. code-block:: bash

   ece4-exp inspect gcm-sr.yml

This shows the full YAML content and its location on disk.

3. Generate Your First Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a coupled GCM experiment:

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

**What this does:**

* Uses the GCM standard resolution recipe
* Allocates 1120 processors (10 nodes on MareNostrum5)
* Creates experiment ID ``a001``
* Outputs to ``a001_experiment.yml``

**Required parameters:**

* ``--recipe`` - Which experiment pattern to use
* ``--sim-procs`` - Number of processors for simulation job
* ``--expid`` - 4-character experiment ID (e.g., ``a001``, ``test``, ``gcm4``)

4. Check the Generated File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your configuration is ready:

.. code-block:: bash

   ls -lh a001_experiment.yml
   # -rw-r--r-- 1 user group 25K Jun 11 10:00 a001_experiment.yml

The file contains:

* Complete experiment configuration (~900 lines)
* Processor distribution across components
* Platform launcher settings
* All required EC-Earth4 fields

5. Validate the Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check that everything is correct:

.. code-block:: bash

   ece4-exp validate a001_experiment.yml

Output:

.. code-block:: text

   ✓ Valid YAML syntax
   ✓ Required fields present
   ✓ Component configuration valid
   ✓ Configuration is valid

Common Recipes
--------------

**Coupled GCM (Atmosphere + Ocean)**

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid g001

* Components: OIFS + NEMO + XIOS + OASIS + RNFM
* Resolution: TL255L91 + eORCA1L75
* Processors: 1120 (10 nodes on MareNostrum5)

**Ocean-Only (OMIP)**

.. code-block:: bash

   ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid o001

* Components: NEMO + XIOS
* Forcing: ERA5
* Processors: 224 (2 nodes on MareNostrum5)

**Atmosphere-Only (AMIP)**

.. code-block:: bash

   ece4-exp generate --recipe amip-sr.yml --sim-procs 896 --expid a001

* Components: OIFS + XIOS + AMIPFR
* SST: Prescribed
* Processors: 896 (8 nodes on MareNostrum5)

**Carbon Cycle**

.. code-block:: bash

   ece4-exp generate --recipe ccycle-sr.yml --sim-procs 1120 --expid c001

* Components: OIFS + NEMO + LPJG + XIOS + OASIS
* Includes land surface model
* Processors: 1120+

Setting Up User Defaults
-------------------------

Avoid typing common parameters every time:

.. code-block:: bash

   # Initialize defaults file
   ece4-exp setup

   # Edit with your settings
   vim ~/.config/ece4-exp/defaults.yml

Example defaults:

.. code-block:: yaml

   # Platform settings
   platform: bsc-marenostrum5
   launcher: slurm-wrapper-taskset

   # Your account
   account: bsc32
   # walltime: Set automatically in platform configs (CPLD:1h, OMIP:30min, AMIP:30min)

   # EC-Earth4 version
   repo_owner: ec-earth
   repo_branch: v4.1.8

Now you only need to specify experiment-specific parameters:

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

Preview Before Creating
------------------------

Use ``--dry-run`` to see what would be generated:

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001 --dry-run

This prints the configuration to stdout without writing a file.

Custom Output File
------------------

Specify a custom output filename:

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001 -o my-config.yml

Interactive Demo
----------------

Run the full interactive demo:

.. code-block:: bash

   ./QUICK_DEMO.sh

This walks through:

1. Listing recipes
2. Generating a GCM experiment
3. Modifying and saving as custom recipe
4. Validating the configuration

Takes about 3 minutes.

Common Patterns
---------------

**Generate multiple experiments:**

.. code-block:: bash

   for id in exp{1..5}; do
     ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid $id
   done

**Different resolutions:**

.. code-block:: bash

   # Standard resolution
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid sr01

   # High resolution (custom recipe)
   ece4-exp generate --recipe gcm-hr.yml --sim-procs 4480 --expid hr01

**Platform-specific:**

.. code-block:: bash

   # MareNostrum 5
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid mn01 \\
     --platform bsc-marenostrum5

   # ECMWF
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1024 --expid ec01 \\
     --platform ecmwf-hpc2020 --account spesiexp

Next Steps
----------

Now that you've generated your first configuration:

1. **Learn about recipes**: :doc:`recipes`
2. **Explore all commands**: :doc:`user_guide`
3. **Create custom recipes**: :doc:`workflows`
4. **Read full documentation**: :doc:`user_guide`

Troubleshooting
---------------

**"ERROR: Missing required parameters"**

You need to provide platform settings. Either:

* Add CLI flags: ``--platform bsc-marenostrum5 --account bsc32``
* Or set user defaults: ``ece4-exp setup`` and edit the file

**"Invalid expid"**

Experiment IDs must be exactly 4 alphanumeric characters:

* ✓ Valid: ``a001``, ``test``, ``exp1``, ``gcm4``
* ✗ Invalid: ``a1`` (too short), ``experiment`` (too long), ``exp-1`` (hyphen not allowed)

**"Recipe not found"**

Check available recipes: ``ece4-exp list``

**Need more help?**

* Full guide: :doc:`user_guide`
* API reference: :doc:`api_reference`
* GitHub issues: https://github.com/vlap/ece4-exp/issues
