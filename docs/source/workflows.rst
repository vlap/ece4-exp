Workflows
=========

Common workflows and use patterns for |ece4exp|.

Basic Workflow
--------------

Standard experiment setup:

.. code-block:: bash

   # 1. Choose recipe
   ece4-exp list

   # 2. Generate config
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid a001

   # 3. Validate
   ece4-exp validate a001_experiment.yml

   # 4. Run with EC-Earth4
   cd /path/to/ecearth4/scripts/runtime
   ./se user.yml platform.yml a001_experiment.yml scriptlib/main.yml

Team Collaboration
------------------

Sharing Standard Configs
~~~~~~~~~~~~~~~~~~~~~~~~~

Create team recipes:

.. code-block:: bash

   # Team member creates recipe
   ece4-exp save --expid team --recipe gcm-sr.yml

   # Share with team
   cp ~/.config/ece4-exp/recipes/team.yml /shared/team/recipes/

   # Team members import
   cp /shared/team/recipes/team.yml ~/.config/ece4-exp/recipes/

   # Everyone uses same config
   ece4-exp generate --recipe team.yml --sim-procs 1120 --expid run1

Standardizing Defaults
~~~~~~~~~~~~~~~~~~~~~~

Team-wide defaults file:

.. code-block:: bash

   # Create team defaults template
   cat > /shared/team/defaults.yml << 'EOF'
   platform: bsc-marenostrum5
   launcher: slurm-wrapper-taskset
   account: bsc32
   repo_owner: ec-earth
   repo_branch: v4.1.8
   # walltime: Set automatically in platform configs (CPLD:1h, OMIP:30min, AMIP:30min)
   EOF

   # Team members copy
   mkdir -p ~/.config/ece4-exp
   cp /shared/team/defaults.yml ~/.config/ece4-exp/

Experiment Series
-----------------

Sensitivity Studies
~~~~~~~~~~~~~~~~~~~

Generate multiple variants:

.. code-block:: bash

   # Base experiment
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid base

   # High resolution variant
   ece4-exp generate --recipe gcm-hr.yml --sim-procs 4480 --expid hihr

   # Different forcing
   ece4-exp generate --recipe omip-sr.yml --sim-procs 224 --expid ocfr

Ensemble Runs
~~~~~~~~~~~~~

Generate ensemble members:

.. code-block:: bash

   for member in {01..10}; do
     ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \\
       --expid e$member --description "Ensemble member $member"
   done

Time Period Experiments
~~~~~~~~~~~~~~~~~~~~~~~

Historical + future:

.. code-block:: bash

   # Historical (1850-2014)
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \\
     --expid hist --description "Historical 1850-2014"

   # SSP scenarios
   for ssp in ssp126 ssp245 ssp585; do
     ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 \\
       --expid $ssp --description "Scenario $ssp 2015-2100"
   done

Development Workflow
--------------------

Iterative Testing
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Start with low resolution
   ece4-exp generate --recipe dev-test.yml --sim-procs 224 --expid dev1

   # 2. Test and iterate
   # ... run experiment, find issues ...

   # 3. Save working config
   ece4-exp save --expid dev1 --recipe dev-test.yml

   # 4. Scale up to production
   ece4-exp generate --recipe dev1.yml --sim-procs 1120 --expid prod

Code Changes
~~~~~~~~~~~~

Test code modifications:

.. code-block:: bash

   # Before changes
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid ctrl

   # After code changes
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test

   # Compare configs (should be identical)
   diff ctrl_experiment.yml test_experiment.yml

Automated Workflows
-------------------

Batch Generation
~~~~~~~~~~~~~~~~

Generate many experiments:

.. code-block:: bash

   #!/bin/bash
   # gen-experiments.sh

   RECIPE="gcm-sr.yml"
   PROCS=1120
   PLATFORM="bsc-marenostrum5"
   ACCOUNT="bsc32"

   # Read experiment list from file
   while read expid description; do
     ece4-exp generate --recipe $RECIPE --sim-procs $PROCS \\
       --expid $expid --platform $PLATFORM --account $ACCOUNT \\
       --description "$description"
   done < experiments.txt

Pipeline Integration
~~~~~~~~~~~~~~~~~~~~

Integrate with job submission:

.. code-block:: bash

   #!/bin/bash
   # submit-experiment.sh

   EXPID=$1

   # Generate config
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid $EXPID

   # Validate
   if ! ece4-exp validate ${EXPID}_experiment.yml; then
     echo "Validation failed!"
     exit 1
   fi

   # Submit to EC-Earth4
   cd /path/to/ecearth4/scripts/runtime
   ./se user.yml platform.yml ${EXPID}_experiment.yml scriptlib/main.yml

Multi-Platform Workflow
-----------------------

Testing Portability
~~~~~~~~~~~~~~~~~~~

Generate for different platforms:

.. code-block:: bash

   # MareNostrum 5
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid mn01 \\
     --platform bsc-marenostrum5 --account bsc32

   # ECMWF
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1024 --expid ec01 \\
     --platform ecmwf-hpc2020 --account spesiexp

   # Verify processor distributions match platform capabilities

Platform Migration
~~~~~~~~~~~~~~~~~~

Move experiments between platforms:

.. code-block:: bash

   # Export from old platform
   ece4-exp inspect my-experiment.yml > experiment-settings.txt

   # Generate on new platform
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid mig1 \\
     --platform new-platform --account new-account

   # Compare and adjust as needed

Version Control Integration
---------------------------

Track Recipe Changes
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Initialize git for recipes
   cd ~/.config/ece4-exp/recipes
   git init
   git add *.yml
   git commit -m "Initial recipes"

   # After changes
   git diff  # See what changed
   git commit -am "Update production recipe"

   # Tag stable versions
   git tag -a v1.0 -m "Production v1.0"

Repository Structure
~~~~~~~~~~~~~~~~~~~~

Recommended structure for team repositories:

.. code-block:: text

   team-configs/
   ├── recipes/
   │   ├── production-gcm.yml
   │   ├── testing-gcm.yml
   │   └── development.yml
   ├── defaults/
   │   ├── marenostrum5.yml
   │   └── ecmwf.yml
   └── scripts/
       ├── gen-ensemble.sh
       └── submit-experiment.sh

Recipe Development
------------------

Test-Driven Recipe Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Define requirements
   cat > recipe-requirements.txt << 'EOF'
   - High resolution (T511)
   - Monitoring enabled
   - ECmean activated
   - 4480 processors
   EOF

   # 2. Create recipe
   vim ~/.config/ece4-exp/recipes/high-res.yml

   # 3. Test
   ece4-exp generate --recipe high-res.yml --sim-procs 4480 --expid test --dry-run

   # 4. Validate output matches requirements
   grep "TL511L91" test_experiment.yml
   grep "activate: true" test_experiment.yml

   # 5. Iterate until correct

Recipe Versioning
~~~~~~~~~~~~~~~~~

Track recipe versions:

.. code-block:: bash

   # Version in filename
   gcm-sr-v1.yml
   gcm-sr-v2.yml

   # Or use git tags
   git tag recipe-v1.0 -m "Stable recipe version 1.0"

Migration Workflows
-------------------

From Manual Configs
~~~~~~~~~~~~~~~~~~~

Convert manual configurations to recipes:

.. code-block:: bash

   # 1. Find differences from base
   diff experiment-config-example.yml my-manual-config.yml > changes.diff

   # 2. Extract just the changed values
   # Create minimal recipe with only those changes

   # 3. Test
   ece4-exp generate --recipe extracted.yml --sim-procs 1120 --expid test

   # 4. Verify output matches original
   diff my-manual-config.yml test_experiment.yml

From Other Tools
~~~~~~~~~~~~~~~~

If migrating from other config tools:

1. Identify the experiment pattern
2. Find closest built-in recipe
3. Generate and compare
4. Create custom recipe for differences
5. Test thoroughly

Documentation Workflow
----------------------

Document Your Recipes
~~~~~~~~~~~~~~~~~~~~~~

Add README to recipe directory:

.. code-block:: bash

   cat > ~/.config/ece4-exp/recipes/README.md << 'EOF'
   # Team Recipes

   ## production-gcm.yml
   Standard production coupled GCM
   - Resolution: TL255L91 + eORCA1L75
   - Processors: 1120
   - Monitoring: enabled

   ## testing-gcm.yml
   Testing version with short runs
   - Resolution: TL159L91 + ORCA1L75
   - Processors: 448
   - Monitoring: disabled

   ## high-res.yml
   High resolution for special studies
   - Resolution: TL511L91 + eORCA025L75
   - Processors: 4480
   - Use sparingly due to cost
   EOF

Recipe Catalog
~~~~~~~~~~~~~~

Maintain catalog of available recipes:

.. code-block:: bash

   # Generate catalog
   for recipe in ~/.config/ece4-exp/recipes/*.yml; do
     echo "## $(basename $recipe)"
     ece4-exp inspect $recipe | head -20
     echo ""
   done > recipe-catalog.md

Best Practices
--------------

1. **One recipe per use case** - Don't create too many variants

2. **Descriptive naming** - Use clear, consistent names

3. **Version control** - Track changes to recipes and configs

4. **Test before production** - Always validate generated configs

5. **Document decisions** - Explain why a recipe exists

6. **Share with team** - Keep team recipes in shared location

7. **Regular review** - Periodically clean up unused recipes

8. **Standardize workflows** - Create scripts for common tasks

Troubleshooting Workflows
--------------------------

**Configs differ between team members:**

Check:

1. Same recipe version?
2. Same user defaults?
3. Same ece4-exp version?

.. code-block:: bash

   # Compare recipes
   diff ~/.config/ece4-exp/recipes/team.yml /shared/team/recipes/team.yml

   # Check versions
   pip show ece4-exp

**Automated generation fails:**

Add error handling:

.. code-block:: bash

   if ! ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test; then
     echo "Generation failed! Check parameters."
     exit 1
   fi

**Recipe doesn't work on new platform:**

Platform-specific settings may need adjustment. Regenerate with new platform parameters.

For more examples, see the complete guide: ``docs/GUIDE.md`` in the repository.
