Changelog
=========

All notable changes to |ece4exp| are documented here.

Version 1.3.0 (2026-06-11)
--------------------------

Bug Fixes
~~~~~~~~~

* **Fixed ``ece4-exp save`` completely broken**: ``save_recipe_from_diff.py`` was missing a ``main()`` function,
  causing ``ece4-exp save`` to crash with ``AttributeError`` on every invocation.

* **Fixed save command ignoring ``--config`` path**: ``create_recipe_from_diff`` looked for
  ``{expid}_experiment.yml`` in the current working directory regardless of where the file was generated.
  Now accepts an explicit ``modified_file`` path. Added ``--config`` flag to ``ece4-exp save``.

* **Fixed pristine file written to wrong directory**: When using ``-o /absolute/path/a001.yml``,
  the pristine copy ended up in ``/absolute/path/`` instead of ``~/.config/ece4-exp/``, breaking
  subsequent ``save``. Fixed by always using ``Path(output_file).name`` to build the pristine path.

* **Fixed ``--quiet`` flag not suppressing color in node-conversion log**: ``set_quiet_mode()`` was
  called after the first ``log_info()`` in ``cmd_generate``. Now applied at the start of the function.

* **Fixed recipe TAB completion returning nothing**: The positional ``recipe`` argument had no
  argcomplete completer registered. Added ``_recipe_completer()`` to both ``generate`` and ``inspect``.

* **Fixed stale ``BASE_CONFIG_EXAMPLE`` constant**: Path evaluated at import time, before the
  EC-Earth4 repo was cloned. Replaced with ``get_base_config_example()`` called after clone.

Improvements
~~~~~~~~~~~~

* **Module rename**: ``generate-experiment-config.py`` → ``generate_experiment_config.py``,
  ``validate-experiment-config.py`` → ``validate_experiment_config.py``. Removes ``importlib``
  hacks; modules are now directly importable.

* **``cmd_save`` refactored**: No longer rewrites ``sys.argv`` to call its own module. Calls
  ``create_recipe_from_diff()`` directly.

* **EC-Earth4 version stamp in generated configs**: Generated files now include
  ``experiment._ece4_version: <branch>`` so scientists know which version produced the config.

* **104 unit tests added**: Covers YAML merge logic, node-evaluation expressions, expid validation,
  launcher-kind auto-detection, CLI argument routing, save/overlay roundtrip, and the full
  generate pipeline (no network access required — base config injected as fixture).

* **CI expanded**: Tests all four built-in recipes, both platforms, backward-compat interface,
  and runs the unit test suite on Python 3.9–3.12 / Linux + macOS.

**Installation**: ``pip install --upgrade ece4-exp``

Version 1.2.0 (2026-06-11)
--------------------------

Major UX Improvements
~~~~~~~~~~~~~~~~~~~~~

* **Nodes-first interface**: Specify nodes instead of processors

  * Old: ``ece4-exp generate gcm-sr 1120 a001`` (must calculate 10 × 112)
  * New: ``ece4-exp generate gcm-sr 10 a001`` (just say 10 nodes)
  * Auto-calculates processors based on platform (MN5: 112/node, ECMWF: 128/node)
  * Backward compatible: ``--sim-procs`` still works

* **Simplified documentation**: 50% reduction (2253 → 1214 lines)

  * Merged 7 doc files → 2 (index.rst + reference.rst)
  * All commands with use cases and examples
  * Clear, concise, focused on getting started
  * Old docs preserved in docs/source/old-docs/

Improvements
~~~~~~~~~~~~

* Updated README with nodes-first examples
* Enhanced completion with node suggestions (2, 4, 8, 10, 16, 20, 32, 40)
* Better error messages showing nodes instead of processors
* Comprehensive command reference with real-world use cases

**Installation**: ``pip install --upgrade ece4-exp``

**Migration**: No breaking changes - old style still works!

Version 1.1.2 (2026-06-11)
--------------------------

Critical Fix
~~~~~~~~~~~~

* **Fixed missing recipes and platforms in pip package**: Built-in recipes and platform configs were not included in pip-installed packages

  * Moved ``recipes/`` and ``platforms/`` inside ``ece4_exp/`` package directory
  * Updated packaging configuration to include them as package data
  * All 6 built-in recipes now available: gcm-sr, omip-sr, amip-sr, ccycle-sr, aa2s, OMIP_with_ERA5_6_Cycles
  * Both platform configs now available: bsc-marenostrum5, ecmwf-hpc2020
  * **Impact**: v1.1.0 and v1.1.1 pip users had NO built-in recipes (only worked from source)

Improvements
~~~~~~~~~~~~

* **Enhanced ``list`` command**: Shows ``(empty)`` or ``(N custom)`` status for user directories

  * Makes it clear that empty user directories are expected behavior
  * Example: ``User recipes: ~/.config/ece4-exp/recipes (empty)``

**Installation**: ``pip install --upgrade ece4-exp``

Version 1.1.1 (2026-06-11)
--------------------------

Bug Fixes
~~~~~~~~~

* **Fixed pristine file location**: Pristine copies now saved to ``~/.config/ece4-exp/`` instead of package directory

  * Previous behavior broke for pip-installed users (read-only site-packages)
  * Fixes ``ece4-exp save`` command to properly extract recipes
  * Cleaned up 7 orphaned pristine files from source directory

* **Fixed shell completion**: Updated bash/zsh completion for new syntax

  * Added support for positional args: ``ece4-exp generate <TAB>`` → recipe names
  * Updated commands: ``setup`` (not just ``init-user``)
  * Updated EC-Earth4 versions: v4.1.8 (latest), v4.1.6, v4.2.0
  * Recipe completion now auto-strips ``.yml`` suffix

**Installation**: ``pip install --upgrade ece4-exp``

Version 1.1.0 (2026-06-11)
--------------------------

**Breaking Changes** (simplified for scientist users):

* **Simplified generate syntax**: Use positional args ``ece4-exp generate RECIPE PROCS EXPID``

  * Old syntax still works: ``--recipe --sim-procs --expid``
  * Recipe names auto-normalized: ``gcm-sr`` and ``gcm-sr.yml`` both work

* **Auto-generated filenames**: Creates ``{expid}_experiment.yml`` instead of ``experiment.yml``
* **Renamed command**: ``init-user`` → ``setup`` (old name still works)
* **Hidden advanced commands**: ``validate``, ``completion``, ``info`` no longer in main help
* **Hidden advanced flags**: ``--launcher``, ``--kind``, ``--repo-owner``, ``--repo-branch``

**Improvements**:

* **README**: Reduced from 261 → 118 lines (55% cut), focused on quick start
* **Help text**: Added examples, typical processor counts, getting-started guide
* **Error messages**: Show helpful suggestions (e.g., "Run 'ece4-exp setup' first")
* **Backward compatibility**: Old flag-based syntax fully supported

**Scientist-first workflow**:

.. code-block:: bash

   ece4-exp setup                    # Configure once
   ece4-exp generate gcm-sr 1120 a001  # Generate experiments

Version 1.0.3 (2026-06-11)
--------------------------

New Features
~~~~~~~~~~~~

* **User platforms support**: Customize and add platform launchers in ``~/.config/ece4-exp/platforms/``

  * User platforms override built-in platforms with same name
  * Easy customization of node layouts, OMP threads, launcher settings
  * Platform search order: User platforms → Built-in platforms

Improvements
~~~~~~~~~~~~

* **Enhanced list command**: Shows user and built-in platform locations
* Documentation updates: Added platform customization examples and workflows

Version 1.0.2 (2026-06-11)
--------------------------

New Features
~~~~~~~~~~~~

* **User recipes system**: Store and manage custom recipes in ``~/.config/ece4-exp/recipes/``

  * User recipes override built-in recipes with same name
  * Appears first in ``ece4-exp list`` output
  * Easy sharing and contribution workflow

* **inspect command**: View recipe contents and their physical location

  * ``ece4-exp inspect <recipe.yml>`` displays full recipe file
  * Shows installation path (helpful for pip-installed packages)
  * Works with both user and built-in recipes

Improvements
~~~~~~~~~~~~

* **Enhanced list command**:

  * Shows both user and built-in recipes separately
  * Displays locations of both recipe directories
  * Includes helpful command tips

* **Enhanced save command**:

  * Saves to user recipes directory by default (``~/.config/ece4-exp/recipes/``)
  * Can override with ``-o`` for custom location
  * Easier recipe creation workflow

* **Streamlined defaults.yml**: Reduced from 112 to 20 lines (83% reduction)

  * Removed excessive comments
  * Cleaner, more maintainable format
  * Added note about user recipes location

Bug Fixes
~~~~~~~~~

* Fixed package name references: Changed remaining "ece4-recipe" references to "ece4-exp"
* Error messages now correctly show ``~/.config/ece4-exp/defaults.yml``
* Comments and docstrings updated

Documentation
~~~~~~~~~~~~~

* **README.md**: Added "Custom Recipes" section with examples
* **docs/GUIDE.md**:

  * "Custom Recipes" section with creation, sharing, and contribution workflows
  * Updated ``save`` command docs to reflect new default behavior
  * Simple ``cp`` workflow for adding external recipes

Version 1.0.1 (2026-06-11)
--------------------------

Bug Fixes
~~~~~~~~~

* **Fixed hardcoded development path in message**: Removed ``/home/vlapin/git/ece4-exp/external/...`` reference that didn't work for pip-installed users

* **Added expid validation**: Enforces EC-Earth4 standard of exactly 4 alphanumeric characters (e.g., ``a001``, ``test``, ``gcm4``)

  * Clear error messages with examples when invalid expid provided
  * Validation added to generate, save, and CLI commands
  * Help text updated to explain requirement

Documentation
~~~~~~~~~~~~~

* Updated all examples in README.md to use 4-character expids
* Updated all examples in docs/GUIDE.md to use 4-character expids
* Added note explaining expid requirement

Version 1.0.0 (2026-06-11)
--------------------------

Major Release: Production-Ready Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete refactoring for professional distribution:

* Python CLI entry point (replaces bash wrapper)
* pip/conda installable
* Cross-platform support (Linux, macOS, Windows)
* Comprehensive documentation
* All tests passing

New Features
~~~~~~~~~~~~

* **Python CLI**: ``ece4_exp/cli.py`` replaces bash wrapper

  * Cross-platform support (Windows compatible)
  * Proper console_scripts entry point
  * Better error handling

* **Package structure**:

  * ``pyproject.toml`` configuration
  * ``MANIFEST.in`` for data files
  * Entry point: ``ece4-exp = ece4_exp.cli:main``

* **Commands**:

  * ``list`` - List available recipes
  * ``info`` - Show current configuration
  * ``init-user`` - Initialize user defaults
  * ``generate`` - Generate experiment configuration
  * ``validate`` - Validate configuration
  * ``save`` - Save as recipe

* **Documentation**:

  * Complete README.md
  * Comprehensive docs/GUIDE.md
  * Quick demo script (QUICK_DEMO.sh)
  * Presentation materials

* **GitHub integration**:

  * CI/CD workflows (.github/workflows/)
  * Issue templates
  * Pull request template
  * Contributing guidelines

Breaking Changes
~~~~~~~~~~~~~~~~

* Bash wrapper replaced with Python CLI
* Installation method changed from ``./setup.sh`` to ``pip install``
* Command invocation: ``ece4-exp`` instead of ``./ece4-exp``

Migration Guide
~~~~~~~~~~~~~~~

**From pre-1.0:**

.. code-block:: bash

   # Old way
   git clone ...
   ./setup.sh
   ./ece4-exp generate ...

   # New way
   pip install ece4-exp
   ece4-exp generate ...

**User files**: Configuration location unchanged (``~/.config/ece4-exp/``)

Pre-1.0 Versions (ece4-recipe)
------------------------------

Version 0.x (ece4-recipe)
~~~~~~~~~~~~~~~~~~~~~~~~~

* Original bash-based tool
* Name: ece4-recipe
* Configuration: ``~/.config/ece4-recipe/``
* Installation: Clone and run setup.sh

**Major refactoring (June 2026)**:

* Name change: ece4-recipe → ece4-exp
* Module: ``ece4_recipe/`` → ``ece4_exp/``
* User config: ``~/.config/ece4-recipe/`` → ``~/.config/ece4-exp/``

Development History
-------------------

The tool evolved through several phases:

1. **Initial prototype** - Basic bash scripts for config generation
2. **ece4-recipe** - First structured version with YAML overlays
3. **ece4-exp 1.0** - Complete rewrite as proper Python package
4. **ece4-exp 1.0.2** - User recipe system and improvements

Upgrade Instructions
--------------------

From 1.0.0/1.0.1 to 1.0.2
~~~~~~~~~~~~~~~~~~~~~~~~~

Simple upgrade, no breaking changes:

.. code-block:: bash

   pip install --upgrade ece4-exp

New features are opt-in. Existing workflows continue working.

From pre-1.0 to 1.0+
~~~~~~~~~~~~~~~~~~~~

1. **Uninstall old version**:

   .. code-block:: bash

      # Remove old installation
      rm -rf /path/to/old/ece4-recipe

2. **Migrate user config** (if using old ece4-recipe):

   .. code-block:: bash

      # Rename config directory
      mv ~/.config/ece4-recipe ~/.config/ece4-exp

3. **Install new version**:

   .. code-block:: bash

      pip install ece4-exp

4. **Update any scripts**:

   .. code-block:: bash

      # Old
      ./ece4-exp generate ...

      # New
      ece4-exp generate ...

Deprecation Notices
-------------------

* **Bash wrapper removed** (v1.0.0): Use Python CLI instead
* **ece4-recipe name** (v1.0.0): Project renamed to ece4-exp

Roadmap
-------

Planned for Future Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **More built-in recipes**: Additional experiment patterns
* **More platforms**: CSC Mahti, DKRZ Levante, etc.
* **Recipe templates**: Interactive recipe creation wizard
* **Configuration validation**: Enhanced schema checking
* **Performance improvements**: Faster git sparse checkout
* **Integration**: Better Autosubmit integration

See GitHub issues for detailed feature requests: https://github.com/vlap/ece4-exp/issues

Contributing
------------

We welcome contributions! See ``CONTRIBUTING.md`` in the repository for guidelines.

To report bugs or request features: https://github.com/vlap/ece4-exp/issues

License
-------

|ece4exp| is released under the MIT License. See LICENSE file for details.
