"""
Session-scoped fixtures that make the test suite self-contained:

1. Writes minimal ~/.config/ece4-exp/defaults.yml for CLI tests on a clean runner.
2. Seeds experiment-config-example.yml and ecearth4 platform files in the cache.
3. Sets ECE4_SKIP_SYNC so tests never clone git.smhi.se.
"""
import os
import pytest
from pathlib import Path
from ece4_exp import paths

_BASE_CONFIG = """\
ece4:
  experiment:
    id: XXXX
    description: A new ECE4 experiment
    schedule:
      all: !rrule >
        DTSTART:18500101 RRULE:FREQ=YEARLY;INTERVAL=1;UNTIL=18510101
      nlegs: 1
    run_from_scratch: false
  model_config:
    components: []
  job:
    launch:
      method: slurm-wrapper-taskset
    resubmit: true
    slurm:
      sbatch:
        opts:
          time: "00:30:00"
          output: XXXX.log
          job-name: ECE4_XXXX
"""

# Minimal ecearth4 platform files — provide cpus_per_node and default qos
# so generate_config() can resolve them without a real git clone.
_ECE4_PLATFORMS = {
    "bsc-marenostrum5-intel+intelmpi.yml": """\
- base.context:
    platform:
      name: bsc-marenostrum5-intel+intelmpi
      cpus_per_node: 112
    job:
      slurm:
        sbatch:
          opts:
            qos: gp_bsces
""",
    "ecmwf-hpc2020-intel+openmpi.yml": """\
- base.context:
    platform:
      name: ecmwf-hpc2020-intel+openmpi
      cpus_per_node: 128
    job:
      slurm:
        sbatch:
          opts:
            qos: np
""",
}


@pytest.fixture(autouse=True, scope="session")
def ci_environment(tmp_path_factory):
    """Prepare a self-contained environment for the test suite."""

    # --- 1. defaults.yml ---
    defaults_file = paths.USER_DEFAULTS_FILE
    created_defaults = False
    if not defaults_file.exists():
        paths.USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        paths.USER_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
        paths.USER_PLATFORMS_DIR.mkdir(parents=True, exist_ok=True)
        defaults_file.write_text(
            "platform: bsc-marenostrum5\n"
            "launcher: slurm-wrapper-taskset\n"
            "kind: auto\n"
            "repo_owner: ec-earth\n"
            "repo_branch: v4.1.8\n"
            "account: testaccount\n"
        )
        created_defaults = True

    # --- 2. Seed base config ---
    cache_runtime = paths.ECE4_CACHE_REPO / "scripts" / "runtime"
    base_config = cache_runtime / "experiment-config-example.yml"
    created_base = False
    if not base_config.exists():
        cache_runtime.mkdir(parents=True, exist_ok=True)
        base_config.write_text(_BASE_CONFIG)
        created_base = True

    # --- 3. Seed ecearth4 platform files ---
    cache_platforms = paths.ECE4_CACHE_REPO / "scripts" / "platforms"
    created_platforms = []
    cache_platforms.mkdir(parents=True, exist_ok=True)
    for fname, content in _ECE4_PLATFORMS.items():
        p = cache_platforms / fname
        if not p.exists():
            p.write_text(content)
            created_platforms.append(p)

    # --- 4. Skip git sync for the whole test session ---
    os.environ["ECE4_SKIP_SYNC"] = "1"

    yield

    # Tear down only what we created
    os.environ.pop("ECE4_SKIP_SYNC", None)
    if created_defaults and defaults_file.exists():
        defaults_file.unlink()
    if created_base and base_config.exists():
        base_config.unlink()
    for p in created_platforms:
        if p.exists():
            p.unlink()
