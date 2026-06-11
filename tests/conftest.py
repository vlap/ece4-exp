"""
Session-scoped fixture that writes a minimal defaults.yml so CLI tests
work on a clean CI runner with no ~/.config/ece4-exp/ directory.
"""
import pytest
from pathlib import Path
from ece4_exp import paths


@pytest.fixture(autouse=True, scope="session")
def minimal_user_defaults(tmp_path_factory):
    """Create ~/.config/ece4-exp/defaults.yml with the minimum required fields.

    This makes CLI tests that call 'ece4-exp generate ... --dry-run' work on a
    fresh CI runner that has never run 'ece4-exp setup'.  The fixture is
    autouse so every test benefits without having to request it explicitly.
    """
    config_dir = paths.USER_CONFIG_DIR
    defaults_file = paths.USER_DEFAULTS_FILE

    # Only write if the file doesn't already exist (respect real user config)
    if not defaults_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
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
        created = True
    else:
        created = False

    yield

    # Clean up only what we created (don't remove a real user's config)
    if created and defaults_file.exists():
        defaults_file.unlink()
