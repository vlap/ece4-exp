API Reference
=============

This page documents the Python API for |ece4exp|. Most users will use the command-line interface, but the Python API is available for programmatic use.

Command-Line Interface
----------------------

The main entry point is ``ece4_exp.cli:main()``.

.. code-block:: python

   from ece4_exp import cli

   # Programmatically run commands
   import sys
   sys.argv = ['ece4-exp', 'list']
   cli.main()

Core Modules
------------

paths
~~~~~

Module: ``ece4_exp.paths``

Defines paths to recipes, platforms, and user configuration.

.. code-block:: python

   from ece4_exp import paths

   # Key paths
   print(paths.RECIPES_DIR)        # Built-in recipes
   print(paths.USER_RECIPES_DIR)   # User recipes
   print(paths.PLATFORMS_DIR)      # Platform launchers
   print(paths.USER_DEFAULTS_FILE) # User defaults

Functions:

* ``get_recipe_path(recipe_name)`` - Find recipe (user → built-in → absolute)
* ``get_platform_launchers_path(platform_name)`` - Get platform launcher file
* ``get_ecearth4_platform_path(platform_name)`` - Get EC-Earth4 platform file

yaml_util
~~~~~~~~~

Module: ``ece4_exp.yaml_util``

YAML loading, merging, and logging utilities.

.. code-block:: python

   from ece4_exp.yaml_util import load_yaml_config, deep_merge, log_info

   # Load YAML
   config = load_yaml_config('config.yml')

   # Merge configs
   merged = deep_merge(base_config, overlay_config)

   # Logging
   log_info("Processing complete")
   log_warn("Warning message")
   log_error("Error message")

Functions:

* ``load_yaml_config(file_path)`` - Load YAML file with error handling
* ``deep_merge(base, overlay)`` - Deep merge two dictionaries
* ``log_info(message)`` - Log info message with colors
* ``log_warn(message)`` - Log warning message
* ``log_error(message)`` - Log error message
* ``set_quiet_mode(quiet)`` - Disable colored output

generate-experiment-config
~~~~~~~~~~~~~~~~~~~~~~~~~~

Module: ``ece4_exp.generate-experiment-config``

Core config generation logic.

.. code-block:: python

   import importlib
   gec = importlib.import_module('ece4_exp.generate-experiment-config')

   # Main function (typically called via CLI)
   gec.main()

Key functions:

* ``generate_config(...)`` - Generate experiment configuration
* ``clone_ece4_yml_repo(...)`` - Clone EC-Earth4 config repository
* ``load_user_defaults()`` - Load user defaults file

validate-experiment-config
~~~~~~~~~~~~~~~~~~~~~~~~~~

Module: ``ece4_exp.validate-experiment-config``

Configuration validation.

.. code-block:: python

   import importlib
   vec = importlib.import_module('ece4_exp.validate-experiment-config')

   # Validate config file
   sys.argv = ['validate', 'config.yml']
   vec.main()

save_recipe_from_diff
~~~~~~~~~~~~~~~~~~~~~

Module: ``ece4_exp.save_recipe_from_diff``

Save modifications as recipes.

.. code-block:: python

   from ece4_exp import save_recipe_from_diff

   # Called via CLI
   # Extracts differences between generated config and base recipe

init_config
~~~~~~~~~~~

Module: ``ece4_exp.init_config``

User configuration initialization.

.. code-block:: python

   from ece4_exp.init_config import initialize_user_config

   # Create default config file
   initialize_user_config()

Programmatic Usage Examples
----------------------------

Generate Config Programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import sys
   from ece4_exp import cli

   # Set CLI arguments
   sys.argv = [
       'ece4-exp', 'generate',
       '--recipe', 'gcm-sr.yml',
       '--sim-procs', '1120',
       '--expid', 'test',
       '--platform', 'bsc-marenostrum5',
       '--account', 'bsc32'
   ]

   # Run
   cli.main()

List Recipes Programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ece4_exp import paths
   from pathlib import Path

   # Get built-in recipes
   builtin_recipes = list(paths.RECIPES_DIR.glob('*.yml'))

   # Get user recipes
   if paths.USER_RECIPES_DIR.exists():
       user_recipes = list(paths.USER_RECIPES_DIR.glob('*.yml'))
   else:
       user_recipes = []

   # Print
   print("Built-in recipes:")
   for r in builtin_recipes:
       print(f"  - {r.name}")

   print("User recipes:")
   for r in user_recipes:
       print(f"  - {r.name}")

Load and Merge Configs
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ece4_exp.yaml_util import load_yaml_config, deep_merge

   # Load configs
   base = load_yaml_config('base.yml')
   recipe = load_yaml_config('recipe.yml')

   # Merge
   merged = deep_merge(base, recipe)

   # Access merged config
   components = merged['model_config']['components']
   print(f"Components: {components}")

Constants and Configuration
----------------------------

Color Constants
~~~~~~~~~~~~~~~

.. code-block:: python

   from ece4_exp.yaml_util import (
       COLOR_RED,
       COLOR_GREEN,
       COLOR_YELLOW,
       COLOR_CYAN,
       COLOR_NC  # Reset
   )

Path Constants
~~~~~~~~~~~~~~

.. code-block:: python

   from ece4_exp import paths

   # Directories
   paths.ROOT_DIR          # Package root
   paths.RECIPES_DIR       # Built-in recipes
   paths.PLATFORMS_DIR     # Platform launchers
   paths.EXTERNAL_DIR      # External cloned repos

   # User paths
   paths.USER_CONFIG_DIR       # ~/.config/ece4-exp
   paths.USER_DEFAULTS_FILE    # ~/.config/ece4-exp/defaults.yml
   paths.USER_RECIPES_DIR      # ~/.config/ece4-exp/recipes
   paths.USER_PLATFORMS_DIR    # ~/.config/ece4-exp/platforms

Data Structures
---------------

Recipe Structure
~~~~~~~~~~~~~~~~

Recipes are YAML files with this structure:

.. code-block:: python

   {
       'base.context': {
           'experiment': {
               'monitoring': {'activate': True},
               'ecmean': {'activate': True, 'frequency': 1}
           },
           'model_config': {
               'components': ['oifs', 'nemo', 'xios', 'oasis'],
               'oifs': {'grid': 'TL255L91', 'precision': 'DP'},
               'nemo': {'grid': 'eORCA1L75_ISO'}
           }
       }
   }

User Defaults Structure
~~~~~~~~~~~~~~~~~~~~~~~

User defaults file (``~/.config/ece4-exp/defaults.yml``):

.. code-block:: python

   {
       'platform': 'bsc-marenostrum5',
       'launcher': 'slurm-wrapper-taskset',
       'kind': 'auto',
       'account': 'bsc32',
       'qos': 'gp_bsces',
       'repo_owner': 'ec-earth',
       'repo_branch': 'v4.1.8'
       # Note: walltime set in platform configs, not user defaults
   }

Error Handling
--------------

The package uses ``sys.exit()`` for errors in CLI mode. When using programmatically, catch ``SystemExit``:

.. code-block:: python

   import sys
   from ece4_exp import cli

   try:
       sys.argv = ['ece4-exp', 'generate', '--invalid']
       cli.main()
   except SystemExit as e:
       if e.code != 0:
           print(f"Command failed with code {e.code}")

Testing
-------

Test the package:

.. code-block:: python

   # Test recipe discovery
   from ece4_exp import paths
   assert paths.RECIPES_DIR.exists()

   # Test YAML loading
   from ece4_exp.yaml_util import load_yaml_config
   config = load_yaml_config(paths.RECIPES_DIR / 'gcm-sr.yml')
   assert 'base.context' in config

   # Test path resolution
   recipe_path = paths.get_recipe_path('gcm-sr.yml')
   assert recipe_path is not None

Extending ece4-exp
------------------

Adding New Commands
~~~~~~~~~~~~~~~~~~~

Edit ``ece4_exp/cli.py`` to add new commands:

.. code-block:: python

   def cmd_my_command(args):
       """My custom command."""
       print("Executing custom command")

   # In main():
   parser_custom = subparsers.add_parser('my-command',
                                          help='My custom command')
   parser_custom.set_defaults(func=cmd_my_command)

Adding New Platforms
~~~~~~~~~~~~~~~~~~~~

Create ``platforms/my-platform.yml``:

.. code-block:: yaml

   slurm-wrapper-taskset:
     CPLD-SR:
       ppn: 128
       launcher:
         binary: srun
       # ... more configuration

The new platform becomes available automatically.

Internal APIs
-------------

These are internal functions not intended for direct use, but documented for developers:

* ``run_git_command(...)`` - Execute git commands safely
* ``calculate_processor_distribution(...)`` - Distribute procs across components
* ``validate_expid(...)`` - Validate experiment ID format

For complete implementation details, see the source code on GitHub: https://github.com/vlap/ece4-exp
