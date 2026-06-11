import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.resolve()
ROOT_DIR    = Path(__file__).parent.parent.resolve()

# Built-in recipes and platforms — bundled in the pip package
RECIPES_DIR   = PACKAGE_DIR / "recipes"
PLATFORMS_DIR = PACKAGE_DIR / "platforms"

# User config directory
USER_CONFIG_DIR   = Path.home() / ".config" / "ece4-exp"
USER_DEFAULTS_FILE = USER_CONFIG_DIR / "defaults.yml"
USER_RECIPES_DIR  = USER_CONFIG_DIR / "recipes"
USER_PLATFORMS_DIR = USER_CONFIG_DIR / "platforms"
USER_CACHE_DIR    = USER_CONFIG_DIR / "cache"
ECE4_CACHE_REPO   = USER_CACHE_DIR / "ecearth4"


def get_base_config_example():
    """Resolve path to experiment-config-example.yml after the repo is cloned."""
    return str(ECE4_CACHE_REPO / "scripts/runtime/experiment-config-example.yml")


def get_ecearth4_platform_path(platform_name):
    """Find the ecearth4 platform file by prefix match (ignores compiler suffix).

    e.g. 'bsc-marenostrum5' matches 'bsc-marenostrum5-intel+intelmpi.yml'.
    Returns the first alphabetical match, or None if not found.
    """
    platforms_dir = ECE4_CACHE_REPO / "scripts/platforms"
    if not platforms_dir.exists():
        return None
    matches = sorted(platforms_dir.glob(f"{platform_name}*.yml"))
    return str(matches[0]) if matches else None


def get_recipe_path(recipe_name):
    """Return path to recipe.

    Search order:
    1. Absolute path
    2. Relative path from CWD (e.g. a001.yml, ./myrecipe.yml)
    3. User recipes (~/.config/ece4-exp/recipes/)
    4. Built-in package recipes
    """
    if not recipe_name:
        return None
    if not recipe_name.endswith((".yml", ".yaml")):
        recipe_name += ".yml"
    if os.path.isabs(recipe_name):
        return recipe_name
    # Check CWD — allows using generated experiment files as recipes
    cwd_path = Path(recipe_name)
    if cwd_path.exists():
        return str(cwd_path.resolve())
    user = USER_RECIPES_DIR / recipe_name
    if user.exists():
        return str(user)
    return str(RECIPES_DIR / recipe_name)


def get_platform_launchers_path(platform_name):
    """Return path to platform launcher file: user platforms first, then built-in."""
    if not platform_name:
        return None
    if not platform_name.endswith((".yml", ".yaml")):
        platform_name += ".yml"
    user = USER_PLATFORMS_DIR / platform_name
    if user.exists():
        return str(user)
    return str(PLATFORMS_DIR / platform_name)
