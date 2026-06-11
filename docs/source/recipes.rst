Recipes
=======

Recipes are YAML files that define experiment patterns. This page describes available recipes and how to create custom ones.

Built-in Recipes
----------------

gcm-sr.yml
~~~~~~~~~~

**Coupled atmosphere-ocean GCM at standard resolution**

.. code-block:: yaml

   Components: OIFS + NEMO + XIOS + OASIS + RNFM
   Resolution: TL255L91 + eORCA1L75
   Processors: 1120 (MareNostrum5: 10 nodes)

**Usage:**

.. code-block:: bash

   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid g001

**Use cases:**

* Standard coupled climate simulations
* Historical runs
* Future scenarios
* Paleo climate studies

omip-sr.yml
~~~~~~~~~~~

**Ocean-only with ERA5 forcing**

.. code-block:: yaml

   Components: NEMO + XIOS
   Forcing: ERA5 atmospheric reanalysis
   Resolution: eORCA1L75
   Processors: 224 (MareNostrum5: 2 nodes)

**Usage:**

.. code-block:: bash

   ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid o001

**Use cases:**

* Ocean model development
* Ocean-only simulations
* OMIP protocol experiments
* Faster turnaround testing

amip-sr.yml
~~~~~~~~~~~

**Atmosphere-only with prescribed SST**

.. code-block:: yaml

   Components: OIFS + XIOS + AMIPFR
   SST: Prescribed from observations
   Resolution: TL255L91
   Processors: 896 (MareNostrum5: 8 nodes)

**Usage:**

.. code-block:: bash

   ece4-exp generate --recipe amip-sr.yml --sim-procs 896 --expid a001

**Use cases:**

* Atmosphere model development
* AMIP protocol experiments
* Faster atmosphere-only runs
* Sensitivity tests

ccycle-sr.yml
~~~~~~~~~~~~~

**Carbon cycle coupled simulation**

.. code-block:: yaml

   Components: OIFS + NEMO + LPJG + XIOS + OASIS
   Resolution: TL255L91 + eORCA1L75
   Processors: 1120+ (MareNostrum5: 10+ nodes)

**Usage:**

.. code-block:: bash

   ece4-exp generate --recipe ccycle-sr.yml --sim-procs 1120 --expid c001

**Use cases:**

* Carbon cycle studies
* Land surface interactions
* Vegetation dynamics
* Biogeochemical cycles

Recipe Structure
----------------

Recipes are minimal YAML files with only the settings that differ from the base configuration.

**Example structure:**

.. code-block:: yaml

   - base.context:
       experiment:
         monitoring:
           activate: true
         ecmean:
           activate: true
           frequency: 1
       model_config:
         components: [oifs, xios, nemo, rnfm, oasis]
         oifs:
           grid: TL255L91
           precision: DP
         oasis:
           load_balancing: 1
         nemo:
           grid: eORCA1L75_ISO

**Key sections:**

* ``experiment`` - Experiment-level settings (monitoring, ecmean)
* ``model_config`` - Component configuration
* ``components`` - Which models to run
* Component-specific - Grid, precision, etc.

Creating Custom Recipes
------------------------

User recipes go in ``~/.config/ece4-exp/recipes/`` and override built-in recipes.

Method 1: Save Modifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start from an existing experiment:

.. code-block:: bash

   # 1. Generate base config
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test

   # 2. Edit the generated file
   vim test_experiment.yml

   # 3. Save as new recipe
   ece4-exp save --expid test --recipe gcm-sr.yml
   # Creates: ~/.config/ece4-exp/recipes/test.yml

   # 4. Use your recipe
   ece4-exp generate --recipe test.yml --sim-procs 1120 --expid prod

Method 2: Create from Scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Write a recipe manually:

.. code-block:: bash

   cat > ~/.config/ece4-exp/recipes/high-res-gcm.yml << 'EOF'
   - base.context:
       model_config:
         components: [oifs, xios, nemo, oasis]
         oifs:
           grid: TL511L91  # Higher resolution
           precision: DP
         nemo:
           grid: eORCA025L75  # 0.25° ocean
   EOF

Method 3: Copy and Modify
~~~~~~~~~~~~~~~~~~~~~~~~~

Start from a built-in recipe:

.. code-block:: bash

   # Find recipe location
   ece4-exp inspect gcm-sr.yml

   # Copy to user recipes
   cp /path/to/installed/gcm-sr.yml ~/.config/ece4-exp/recipes/my-gcm.yml

   # Edit
   vim ~/.config/ece4-exp/recipes/my-gcm.yml

Recipe Examples
---------------

High-Resolution GCM
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ~/.config/ece4-exp/recipes/gcm-hr.yml
   - base.context:
       model_config:
         components: [oifs, xios, nemo, rnfm, oasis]
         oifs:
           grid: TL511L91  # T511 instead of T255
           precision: DP
         nemo:
           grid: eORCA025L75  # 0.25° instead of 1°

**Usage:** 4480 processors (40 nodes)

No Monitoring
~~~~~~~~~~~~~

.. code-block:: yaml

   # ~/.config/ece4-exp/recipes/gcm-nomon.yml
   - base.context:
       experiment:
         monitoring:
           activate: false  # Disable monitoring
         ecmean:
           activate: false  # Disable ecmean
       model_config:
         components: [oifs, xios, nemo, rnfm, oasis]
         oifs:
           grid: TL255L91

Development Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ~/.config/ece4-exp/recipes/dev-test.yml
   - base.context:
       experiment:
         nlegs: 1  # Short run
         monitoring:
           activate: true
       model_config:
         components: [oifs, xios, nemo, oasis]
         oifs:
           grid: TL159L91  # Lower resolution for testing
         nemo:
           grid: ORCA1L75

Sharing Recipes
---------------

With Your Team
~~~~~~~~~~~~~~

.. code-block:: bash

   # Export recipe
   cp ~/.config/ece4-exp/recipes/my-recipe.yml /shared/team/recipes/

   # Import on another machine
   cp /shared/team/recipes/my-recipe.yml ~/.config/ece4-exp/recipes/

Contribute Upstream
~~~~~~~~~~~~~~~~~~~

Share recipes with the community:

.. code-block:: bash

   # 1. Fork repository on GitHub
   # https://github.com/vlap/ece4-exp

   # 2. Clone your fork
   git clone https://github.com/yourusername/ece4-exp.git
   cd ece4-exp

   # 3. Copy your recipe
   cp ~/.config/ece4-exp/recipes/my-recipe.yml recipes/

   # 4. Commit and push
   git add recipes/my-recipe.yml
   git commit -m "Add recipe for <use case>"
   git push origin main

   # 5. Create pull request on GitHub

Recipe Best Practices
---------------------

1. **Minimal content** - Only include settings that differ from base

2. **Clear naming** - Use descriptive filenames (``gcm-hr.yml``, not ``test.yml``)

3. **Document purpose** - Add comments explaining the recipe's use case

4. **Test thoroughly** - Validate generated configs before sharing

5. **Version control** - Track recipe changes if modifying over time

6. **Consistent style** - Follow YAML conventions and existing recipe patterns

Recipe Validation
-----------------

After creating a recipe, test it:

.. code-block:: bash

   # Generate test config
   ece4-exp generate --recipe my-recipe.yml --sim-procs 1120 --expid test --dry-run

   # Check output looks correct
   ece4-exp generate --recipe my-recipe.yml --sim-procs 1120 --expid test

   # Validate
   ece4-exp validate test_experiment.yml

Recipe Troubleshooting
----------------------

**Recipe not found:**

Check:

1. Is it in ``~/.config/ece4-exp/recipes/``?
2. Does the filename match exactly? (case-sensitive)
3. Is it a ``.yml`` or ``.yaml`` file?

.. code-block:: bash

   # List your recipes
   ls -lh ~/.config/ece4-exp/recipes/

**Generated config is wrong:**

Check recipe content:

.. code-block:: bash

   ece4-exp inspect my-recipe.yml

Verify YAML syntax is correct.

**Conflicts with base config:**

User recipes merge with base config. Later layers override earlier ones.

If something isn't working, check the full merged output:

.. code-block:: bash

   ece4-exp generate --recipe my-recipe.yml --sim-procs 1120 --expid test --dry-run

Recipe Reference
----------------

For complete recipe structure and available fields, see:

* EC-Earth4 repository: ``scripts/runtime/experiment-config-example.yml``
* Platform launchers: ``platforms/*.yml`` in ece4-exp repository
* Built-in recipes: ``recipes/*.yml`` in ece4-exp repository

Advanced Recipe Topics
----------------------

**Override specific components:**

.. code-block:: yaml

   model_config:
     oifs:
       grid: TL511L91
       # Other OIFS settings inherited from base

**Add extra monitoring:**

.. code-block:: yaml

   experiment:
     monitoring:
       activate: true
       extra_diagnostics: true

**Platform-specific recipes:**

Recipes can include platform-specific overrides, though this is rarely needed since platforms are handled separately.

For more advanced usage, see the complete guide: ``docs/GUIDE.md`` in the repository.
