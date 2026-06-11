Welcome to ece4-exp's documentation!
=====================================

|ece4exp| is a lightweight tool for generating |ecearth4| experiment configurations in 30 seconds.

**Key Features:**

* 🚀 Generate configs in 30 seconds (vs 30 minutes manually)
* 📦 Pre-built recipes for common experiments (GCM, OMIP, AMIP, carbon cycle)
* 🎯 Simple CLI: ``ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001``
* 🔧 User recipes and platforms in ``~/.config/ece4-exp/`` for customization
* ⚙️ YAML overlay system: Base → Platform → Recipe → User defaults → CLI flags

**Quick Start:**

.. code-block:: bash

   # Install
   pip install ece4-exp

   # Generate your first experiment
   ece4-exp list
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro
   installation
   quickstart
   user_guide
   recipes
   workflows
   api_reference
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
