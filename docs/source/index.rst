Welcome to ece4-exp!
====================

Generate EC-Earth4 experiment configurations in 30 seconds.

.. code-block:: bash

   pip install ece4-exp
   ece4-exp setup                    # First-time configuration
   ece4-exp generate gcm-sr 10 a001  # Generate experiment (10 nodes)

What is ece4-exp?
-----------------

A command-line tool that generates EC-Earth4 experiment configuration files using a YAML overlay system.

**The problem it solves**: Creating an EC-Earth4 experiment config manually means editing a 250-line YAML file, calculating processor distributions, matching components, paths, and accounts — a 2–4 hour job. ece4-exp brings that down to 30 seconds.

**How it works**:

The tool merges five configuration layers into a single validated YAML file:

.. code-block:: text

   1. Base config       (fetched from EC-Earth4 repo, always up-to-date)
        ↓
   2. Platform launcher (node layout, SLURM settings for your HPC)
        ↓
   3. Recipe            (experiment type: GCM, OMIP, AMIP, carbon cycle...)
        ↓
   4. Your defaults     (~/.config/ece4-exp/defaults.yml)
        ↓
   5. CLI flags         (per-run overrides)
        ↓
   Generated config     (a001_experiment.yml, ready to submit)

Each layer overrides the previous. You only specify what differs from defaults.

**Nodes, not processors**: Instead of calculating ``10 nodes × 112 cores/node = 1120``, you just say ``10``. The tool looks up your platform's cores-per-node and does the math.

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

**Shell completion**: After ``ece4-exp setup``, add one line to your shell config:

.. code-block:: bash

   # bash — add to ~/.bashrc
   eval "$(register-python-argcomplete ece4-exp)"

   # zsh — add to ~/.zshrc
   eval "$(register-python-argcomplete ece4-exp)"

Then ``source ~/.bashrc`` (or restart your shell).

Supported Platforms
~~~~~~~~~~~~~~~~~~~

* **BSC MareNostrum 5** — 112 cores/node
* **ECMWF HPC2020** — 128 cores/node
* Custom platforms supported via ``~/.config/ece4-exp/platforms/``

Quick Start
-----------

**1. Setup** (one-time, ~1 minute):

.. code-block:: bash

   ece4-exp setup

Interactive wizard asks for your HPC platform and account. Creates ``~/.config/ece4-exp/defaults.yml``.

**2. List available recipes**:

.. code-block:: bash

   ece4-exp list

**3. Generate your first experiment**:

.. code-block:: bash

   ece4-exp generate gcm-sr 10 a001

This generates ``a001_experiment.yml`` — 10 nodes (1120 cores on MareNostrum5), coupled GCM configuration, ready to submit.

**4. Deploy to HPC and run**:

.. code-block:: bash

   ece4-exp deploy a001    # rsync to HPC scratch/ecearth4/scripts/runtime/

   # then on the HPC:
   cd $scratch/ecearth4/scripts/runtime
   se user.yml platform.yml a001_experiment.yml scriptlib/main.yml

``deploy`` uses ``rsync`` over SSH. Configure ``host`` and ``scratch`` once in
``~/.config/ece4-exp/defaults.yml`` (shown by ``ece4-exp setup``).
The generated file is one of several YAMLs passed to ``se`` — it holds the
experiment-specific settings; the platform and user files load separately.

About Experiment IDs
~~~~~~~~~~~~~~~~~~~~

The EXPID (``a001`` in the example above) is EC-Earth4's standard experiment identifier:

* Exactly **4 alphanumeric characters**: ``a001``, ``test``, ``gcm4``, ``ctrl``
* Used as a prefix for output files, job names, and restart files
* EC-Earth4 enforces this format throughout its scripts

Common Recipes
--------------

.. list-table::
   :header-rows: 1
   :widths: 15 35 30 20

   * - Recipe
     - Description
     - Components
     - Typical Nodes (MN5)
   * - **gcm-sr**
     - Coupled atmosphere-ocean GCM
     - OIFS, NEMO, XIOS, OASIS, RNFM
     - 10 nodes (1120 cores)
   * - **omip-sr**
     - Ocean-only with ERA5 forcing
     - NEMO, XIOS
     - 2 nodes (224 cores)
   * - **amip-sr**
     - Atmosphere-only, prescribed SST
     - OIFS, XIOS, AMIPFR, OASIS
     - 8 nodes (896 cores)
   * - **ccycle-sr**
     - Carbon cycle coupled (with LPJG)
     - OIFS, NEMO, LPJG, XIOS, OASIS
     - 10+ nodes

All recipes use standard resolution (SR): OIFS TL255L91, NEMO eORCA1L75.

Common Examples
---------------

**Standard experiments**:

.. code-block:: bash

   # Coupled GCM (10 nodes)
   ece4-exp generate gcm-sr 10 a001

   # Ocean-only (2 nodes)
   ece4-exp generate omip-sr 2 o001

   # Atmosphere-only (8 nodes, 72h walltime override)
   ece4-exp generate amip-sr 8 atm1 --walltime 72

**Custom settings**:

.. code-block:: bash

   # Override platform (e.g., when running at ECMWF)
   ece4-exp generate gcm-sr 10 test --platform ecmwf-hpc2020

   # Custom output filename
   ece4-exp generate gcm-sr 10 a002 -o my-experiment.yml

   # Preview without writing (dry-run)
   ece4-exp generate gcm-sr 10 a003 --dry-run

**Backward compatibility** (old ``--sim-procs`` style still works):

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

   # Optional: Pre-fill recipe so you can omit it on the command line
   # recipe: gcm-sr

Walltime has sensible per-experiment defaults (set in the platform files):

* CPLD-SR (coupled GCM): 1 hour
* OMIP-SR (ocean-only): 30 minutes
* AMIP-SR (atmosphere-only): 30 minutes
* CCCL-SR (carbon cycle): 1.5 hours

Override with ``--walltime HOURS`` when needed.

**Resolution order**: CLI flags > User defaults (``defaults.yml``) > Platform defaults

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

Developed at Barcelona Supercomputing Center (BSC) for the EC-Earth community.
MIT License — see LICENSE for details.
