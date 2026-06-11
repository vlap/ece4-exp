Welcome to ece4-exp!
====================

Generate EC-Earth4 experiment configurations in 30 seconds.

.. code-block:: bash

   pip install ece4-exp
   ece4-exp setup                  # First-time configuration
   ece4-exp generate gcm-sr 10 a001  # Generate experiment (10 nodes)

What is ece4-exp?
-----------------

A command-line tool that generates EC-Earth4 experiment configurations using a YAML overlay system.

**Why use it?**

* 🚀 **30 seconds** vs 30 minutes (manual configuration)
* 📦 **Pre-built recipes**: gcm-sr, omip-sr, amip-sr, ccycle-sr
* 🎯 **Simple**: Just specify nodes, not processors
* ⚙️ **Auto-calculates**: Processor distribution based on your platform
* 🔧 **Customizable**: User recipes and platform configs

**How it works:**

Merges configurations in order: Base → Platform → Recipe → Your defaults → CLI flags

Installation
------------

**From PyPI** (recommended):

.. code-block:: bash

   pip install ece4-exp

**From source** (development):

.. code-block:: bash

   git clone https://github.com/vlap/ece4-exp.git
   cd ece4-exp
   pip install -e .

**Shell completion**: Already enabled! ``ece4-exp setup`` automatically activates TAB completion. Just restart your shell after setup.

Supported Platforms
~~~~~~~~~~~~~~~~~~~

* **BSC MareNostrum 5** - 112 cores/node
* **ECMWF HPC2020** - 128 cores/node
* Custom platforms supported via ``~/.config/ece4-exp/platforms/``

Quick Start
-----------

**1. Setup** (one-time):

.. code-block:: bash

   ece4-exp setup

Interactive setup asks for your platform and account. Creates ``~/.config/ece4-exp/defaults.yml``.

**2. List available recipes**:

.. code-block:: bash

   ece4-exp list

**3. Generate your first experiment**:

.. code-block:: bash

   ece4-exp generate gcm-sr 10 a001

This generates ``a001_experiment.yml`` with 10 nodes (1120 cores on MareNostrum5).

Common Recipes
--------------

.. list-table::
   :header-rows: 1
   :widths: 15 40 20 25

   * - Recipe
     - Description
     - Components
     - Typical Nodes (MN5)
   * - **gcm-sr**
     - Coupled atmosphere-ocean GCM
     - OIFS, NEMO, XIOS, OASIS
     - 10 nodes (1120 cores)
   * - **omip-sr**
     - Ocean-only with ERA5 forcing
     - NEMO, XIOS
     - 2 nodes (224 cores)
   * - **amip-sr**
     - Atmosphere-only, prescribed SST
     - OIFS, XIOS, AMIPFR
     - 8 nodes (896 cores)
   * - **ccycle-sr**
     - Carbon cycle coupled
     - OIFS, NEMO, LPJG, XIOS, OASIS
     - 10+ nodes

Common Examples
---------------

**Standard experiments**:

.. code-block:: bash

   # Coupled GCM (10 nodes)
   ece4-exp generate gcm-sr 10 a001

   # Ocean-only (2 nodes)
   ece4-exp generate omip-sr 2 o001

   # Atmosphere-only (8 nodes, 72h walltime)
   ece4-exp generate amip-sr 8 atm1 --walltime 72

**Custom settings**:

.. code-block:: bash

   # Override platform
   ece4-exp generate gcm-sr 10 test --platform ecmwf-hpc2020

   # Custom output filename
   ece4-exp generate gcm-sr 10 a002 -o my-experiment.yml

   # Preview without writing
   ece4-exp generate gcm-sr 10 a003 --dry-run

**Backward compatibility** (old style still works):

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

Configuration
-------------

User defaults are stored in ``~/.config/ece4-exp/defaults.yml``:

.. code-block:: yaml

   platform: bsc-marenostrum5
   account: bsc32
   qos: gp_bsces
   repo_branch: v4.1.8

   # Optional: Auto-fill recipe to skip typing
   # recipe: gcm-sr

   # Note: Walltime set automatically per experiment type:
   #   CPLD-SR: 1h, OMIP-SR: 30min, AMIP-SR: 30min, CCCL-SR: 1.5h

Resolution order: CLI flags > User defaults > Platform defaults

Next Steps
----------

.. toctree::
   :maxdepth: 2

   reference
   changelog

* :ref:`genindex`
* :ref:`search`

Need Help?
----------

* **Documentation**: https://ece4-exp.readthedocs.io/
* **GitHub**: https://github.com/vlap/ece4-exp
* **Issues**: https://github.com/vlap/ece4-exp/issues
* **PyPI**: https://pypi.org/project/ece4-exp/

License
-------

MIT License. See LICENSE file for details.

Developed at Barcelona Supercomputing Center (BSC) for the EC-Earth community.
