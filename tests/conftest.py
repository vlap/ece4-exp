"""
Session-scoped fixtures that make the test suite self-contained:

1. Writes a minimal ~/.config/ece4-exp/defaults.yml so CLI tests work on
   a clean CI runner that has never run 'ece4-exp setup'.

2. Seeds a minimal experiment-config-example.yml in the cache directory and
   sets ECE4_SKIP_SYNC so tests never try to clone git.smhi.se.
"""
import os
import pytest
from pathlib import Path
from ece4_exp import paths

# Minimal experiment-config-example.yml that mirrors the real structure
# Used so generate_config() can load a base without network access.
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
            "qos: gp_bsces\n"
        )
        created_defaults = True

    # --- 2. Seed minimal base config so no git clone is needed ---
    cache_runtime = paths.ECE4_CACHE_REPO / "scripts" / "runtime"
    base_config = cache_runtime / "experiment-config-example.yml"
    created_cache = False
    if not base_config.exists():
        cache_runtime.mkdir(parents=True, exist_ok=True)
        base_config.write_text(_BASE_CONFIG)
        created_cache = True

    # --- 3. Skip git sync for the whole test session ---
    os.environ["ECE4_SKIP_SYNC"] = "1"

    yield

    # Tear down only what we created
    os.environ.pop("ECE4_SKIP_SYNC", None)
    if created_defaults and defaults_file.exists():
        defaults_file.unlink()
    if created_cache and base_config.exists():
        base_config.unlink()
