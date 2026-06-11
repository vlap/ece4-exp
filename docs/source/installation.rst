Installation
============

|ece4exp| is a pure Python package that can be installed via pip or conda.

Requirements
------------

* Python 3.8 or later
* ruamel.yaml >= 0.17.0
* jsonschema >= 4.0.0

All platforms (Linux, macOS, Windows) are supported.

Install via pip (Recommended)
------------------------------

The simplest way to install |ece4exp|:

.. code-block:: bash

   pip install ece4-exp

This installs the ``ece4-exp`` command and all dependencies.

**Verify installation:**

.. code-block:: bash

   ece4-exp --help
   ece4-exp list

Install from GitHub
-------------------

For the latest development version:

.. code-block:: bash

   git clone https://github.com/vlap/ece4-exp.git
   cd ece4-exp
   pip install -e .

The ``-e`` flag installs in editable mode, useful for development.

Install via conda
-----------------

.. note::

   conda-forge submission is pending. For now, use pip within a conda environment.

Create a conda environment and install:

.. code-block:: bash

   conda create -n ece4exp python=3.11
   conda activate ece4exp
   pip install ece4-exp

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade ece4-exp

Check your current version:

.. code-block:: bash

   pip show ece4-exp

Uninstalling
------------

To remove |ece4exp|:

.. code-block:: bash

   pip uninstall ece4-exp

User files (``~/.config/ece4-exp/``) are preserved and can be manually removed if desired.

Development Setup
-----------------

For contributing to |ece4exp|:

.. code-block:: bash

   # Clone repository
   git clone https://github.com/vlap/ece4-exp.git
   cd ece4-exp

   # Install in editable mode with dev dependencies
   pip install -e .

   # Run tests
   ece4-exp list
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test --dry-run

   # Build documentation (optional)
   pip install sphinx sphinx_rtd_theme
   cd docs
   make html

Troubleshooting
---------------

**Command not found after installation:**

Ensure your pip installation directory is in your PATH:

.. code-block:: bash

   # Check where pip installs scripts
   python -m site --user-base

   # Add to PATH (add to ~/.bashrc for persistence)
   export PATH="$HOME/.local/bin:$PATH"

**Import errors:**

Verify dependencies are installed:

.. code-block:: bash

   pip install ruamel.yaml jsonschema

**Permission errors:**

Use ``--user`` flag to install in user directory:

.. code-block:: bash

   pip install --user ece4-exp

Testing Your Installation
--------------------------

Run the quick demo to verify everything works:

.. code-block:: bash

   ./QUICK_DEMO.sh

Or test individual commands:

.. code-block:: bash

   # List available recipes
   ece4-exp list

   # View a recipe
   ece4-exp inspect gcm-sr.yml

   # Generate a test config
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test --dry-run

If all commands complete successfully, your installation is ready to use!

Next Steps
----------

After installation:

1. **Initialize user defaults** (optional but recommended):

   .. code-block:: bash

      ece4-exp init-user
      # Edit ~/.config/ece4-exp/defaults.yml with your settings

2. **Try the quickstart tutorial**: :doc:`quickstart`

3. **Read the full guide**: :doc:`user_guide`
