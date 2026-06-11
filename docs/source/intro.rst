Introduction
============

About
-----

|ece4exp| is a lightweight command-line tool for generating |ecearth4| experiment configurations quickly and correctly.

**The Problem:**

Creating an EC-Earth4 experiment configuration traditionally requires:

* Finding the right base configuration template
* Understanding the complex YAML structure (900+ lines)
* Manually calculating processor distributions
* Configuring platform-specific launcher settings
* Ensuring all fields are consistent

This process typically takes **30 minutes** and is error-prone.

**The Solution:**

|ece4exp| provides:

* **Pre-built recipes** for common experiment types (GCM, OMIP, AMIP, carbon cycle)
* **Automatic processor distribution** based on your sim-procs
* **Platform launchers** for BSC MareNostrum 5, ECMWF HPC2020, and more
* **YAML overlay system** merging configs in a predictable order
* **User recipes** for custom configurations

Generate a complete, validated configuration in **30 seconds:**

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

How It Works
------------

|ece4exp| uses a **YAML overlay system** that merges configurations in this order:

1. **Base config** - From EC-Earth4 repository (experiment-config-example.yml)
2. **Platform launcher** - Platform-specific settings (from ``platforms/``)
3. **Recipe** - Experiment pattern (from ``recipes/``)
4. **User defaults** - Your personal defaults (``~/.config/ece4-exp/defaults.yml``)
5. **CLI flags** - Command-line arguments (highest priority)

Each layer can add or override settings from previous layers, giving you full control while maintaining simplicity.

.. code-block:: yaml

   # Example: How layers combine

   # Base (from EC-Earth4 repo)
   experiment:
     nlegs: 1

   # Platform launcher
   slurm:
     partition: main

   # Recipe (gcm-sr.yml)
   model_config:
     components: [oifs, nemo, xios, oasis]
     oifs:
       grid: TL255L91

   # User defaults
   account: bsc32
   # walltime: Set automatically in platform configs (CPLD:1h, OMIP:30min, AMIP:30min)

   # CLI flags
   --expid a001
   --sim-procs 1120

   # = Final merged configuration

Key Features
------------

**Pre-Built Recipes**

* ``gcm-sr.yml`` - Coupled atmosphere-ocean GCM (OIFS+NEMO+XIOS+OASIS)
* ``omip-sr.yml`` - Ocean-only with ERA5 forcing
* ``amip-sr.yml`` - Atmosphere-only with prescribed SST
* ``ccycle-sr.yml`` - Carbon cycle (adds LPJG)

**User Recipe System**

Store custom recipes in ``~/.config/ece4-exp/recipes/``:

* User recipes override built-in recipes
* Easy sharing with colleagues (just copy files)
* Simple contribution workflow to upstream

**Commands**

* ``list`` - Browse available recipes
* ``inspect`` - View recipe contents
* ``generate`` - Create experiment configuration
* ``validate`` - Check configuration validity
* ``save`` - Save modifications as new recipe
* ``init-user`` - Initialize user defaults

Design Philosophy
-----------------

|ece4exp| follows these principles:

1. **Simple things should be simple** - One command for standard cases
2. **Complex things should be possible** - Full control via YAML overlays
3. **Don't repeat yourself** - Set defaults once, reuse everywhere
4. **Progressive disclosure** - README (30s) → Demo (10min) → Full guide
5. **Convention over configuration** - Sensible defaults, minimal required args

Target Users
------------

* **New users** - Get started quickly without learning all EC-Earth4 internals
* **Experienced users** - Save time on repetitive configuration tasks
* **Teams** - Share and standardize experiment configurations
* **Developers** - Integrate into automated workflows

Comparison with Manual Setup
-----------------------------

+------------------------+------------------+----------------------+
| Aspect                 | Manual           | ece4-exp             |
+========================+==================+======================+
| Time to create config  | 30 minutes       | 30 seconds           |
+------------------------+------------------+----------------------+
| Lines to write/edit    | ~50-100 lines    | 1 command            |
+------------------------+------------------+----------------------+
| Error rate             | High             | Low (validated)      |
+------------------------+------------------+----------------------+
| Reusability            | Copy/paste       | Named recipes        |
+------------------------+------------------+----------------------+
| Sharing                | Email files      | Recipe files         |
+------------------------+------------------+----------------------+
| Platform support       | Manual editing   | Built-in launchers   |
+------------------------+------------------+----------------------+
| Processor distribution | Manual calc      | Automatic            |
+------------------------+------------------+----------------------+

How to Cite
-----------

If you use |ece4exp| in your research, please cite:

.. code-block:: bibtex

   @software{ece4exp,
     author       = {Vladimir Lapin},
     title        = {ece4-exp: EC-Earth4 experiment configuration tool},
     year         = {2026},
     publisher    = {Barcelona Supercomputing Center},
     url          = {https://github.com/vlap/ece4-exp},
     note         = {Open-source software, MIT License}
   }

License
-------

|ece4exp| is released under the MIT License. See LICENSE file for details.

Acknowledgments
---------------

Developed at Barcelona Supercomputing Center (BSC) for the EC-Earth community.
