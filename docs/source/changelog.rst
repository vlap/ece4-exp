Changelog
=========

All notable changes to |ece4exp| are documented here.

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
