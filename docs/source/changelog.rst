Changelog
=========

All notable changes to |ece4exp| are documented here.

Version 1.1.0 (2026-06-11)
--------------------------

New Features
~~~~~~~~~~~~

* **``ece4-exp deploy EXPID``**: rsync the generated config to the HPC runtime directory.

  .. code-block:: bash

     ece4-exp deploy a001   # uses host/scratch from defaults.yml

  Configure once in ``~/.config/ece4-exp/defaults.yml``:

  .. code-block:: yaml

     host: bsc032XXX@mn1.bsc.es
     scratch: /gpfs/scratch/bsc32/bsc032XXX

  Supports ``--host``, ``--scratch``, and ``--config`` overrides.

Bug Fixes
~~~~~~~~~

* **Fixed ``ece4-exp save`` completely broken**: ``save_recipe_from_diff.py`` was missing a
  ``main()`` function, causing every invocation to crash with ``AttributeError``.

* **Fixed save looking for config in CWD only**: ``create_recipe_from_diff`` now accepts an
  explicit ``modified_file`` path. Added ``--config`` flag to ``ece4-exp save``.

* **Fixed pristine file written to wrong directory**: When using ``-o /absolute/path.yml``,
  the pristine copy ended up alongside the output instead of in ``~/.config/ece4-exp/``,
  breaking subsequent ``ece4-exp save``.

* **Fixed ``--quiet`` not suppressing color in node-conversion log**: ``set_quiet_mode()``
  was called after the first ``log_info()`` in ``cmd_generate``.

* **Fixed recipe TAB completion returning nothing**: The positional ``recipe`` argument had
  no argcomplete completer. Added ``_recipe_completer()`` to ``generate`` and ``inspect``.

* **Fixed stale ``BASE_CONFIG_EXAMPLE`` path**: Path was evaluated at import time before the
  EC-Earth4 repo was cloned. Replaced with ``get_base_config_example()`` called after clone.

Improvements
~~~~~~~~~~~~

* **104 unit tests**: YAML merge logic, node expressions, expid validation, launcher-kind
  auto-detection, full generate pipeline (no network), save/overlay roundtrip, CLI routing.

* **``ECE4_SKIP_SYNC`` env var**: Set to skip git.smhi.se clone (used by test suite and CI).

* **EC-Earth4 version stamp**: Generated configs include ``experiment._ece4_version: v4.1.8``
  so scientists know which version produced a given config.

* **Module rename**: ``generate-experiment-config.py`` → ``generate_experiment_config.py``,
  ``validate-experiment-config.py`` → ``validate_experiment_config.py``.

* **``cmd_save`` refactored**: No longer rewrites ``sys.argv``; calls
  ``create_recipe_from_diff()`` directly.

* **Nodes-first interface**: Specify nodes instead of processors.

  * Old: ``ece4-exp generate gcm-sr --sim-procs 1120 --expid a001``
  * New: ``ece4-exp generate gcm-sr 10 a001`` (just say 10 nodes)
  * Backward compatible — ``--sim-procs`` still works.

* **CI**: Tests all four built-in recipes, both platforms, unit suite on Python 3.9–3.12 / Linux + macOS.

**Installation**: ``pip install ece4-exp``

Version 1.0.0 (2026-06-11)
--------------------------

Initial release as a proper Python package.

* Python CLI replacing the original bash wrapper
* ``pip install ece4-exp`` / conda installable
* Commands: ``setup``, ``list``, ``generate``, ``inspect``, ``save``, ``validate``
* Built-in recipes: gcm-sr, omip-sr, amip-sr, ccycle-sr
* Platform support: BSC MareNostrum5, ECMWF HPC2020
* User recipes and platforms in ``~/.config/ece4-exp/``
* TAB completion via argcomplete (``register-python-argcomplete ece4-exp``)
* GitHub CI/CD with PyPI publishing

**Pre-1.0**: bash-based prototype named ``ece4-recipe``.
