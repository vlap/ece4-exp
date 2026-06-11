import os
from pathlib import Path

# Base directory: ece4_exp/
# Repo root is 1 level up (for development), or package dir (for pip install)
ROOT_DIR = Path(__file__).parent.parent.resolve()
PACKAGE_DIR = Path(__file__).parent.resolve()

# Main Directories (as Path objects for CLI, keeping string versions for backward compat)
# Recipes and platforms are now inside the package for proper pip packaging
RECIPES_DIR = PACKAGE_DIR / "recipes"
EXTERNAL_DIR = ROOT_DIR / "external"
YML_TOOLS_DIR = PACKAGE_DIR
PLATFORMS_DIR = PACKAGE_DIR / "platforms"
SCRIPTS_DIR = ROOT_DIR / "scripts"
DOCS_DIR = ROOT_DIR / "docs"

# String versions for backward compatibility with existing code
_ROOT_DIR_STR = str(ROOT_DIR)
_RECIPES_DIR_STR = str(RECIPES_DIR)
_EXTERNAL_DIR_STR = str(EXTERNAL_DIR)
_YML_TOOLS_DIR_STR = str(YML_TOOLS_DIR)
_PLATFORMS_DIR_STR = str(PLATFORMS_DIR)

# User config directory
USER_CONFIG_DIR = Path.home() / ".config" / "ece4-exp"
USER_DEFAULTS_FILE = USER_CONFIG_DIR / "defaults.yml"
USER_RECIPES_DIR = USER_CONFIG_DIR / "recipes"
USER_PLATFORMS_DIR = USER_CONFIG_DIR / "platforms"
USER_CACHE_DIR = USER_CONFIG_DIR / "cache"
ECE4_CACHE_REPO = USER_CACHE_DIR / "ecearth4"

# ECE4 repository paths (managed via sparse checkout in user cache)
# Prefer user cache, fallback to package dir for backward compatibility
_ECE4_CACHE_BASE = ECE4_CACHE_REPO if ECE4_CACHE_REPO.exists() else EXTERNAL_DIR / "ece4_yml_repo"
BASE_CONFIG_EXAMPLE = str(_ECE4_CACHE_BASE / "scripts/runtime/experiment-config-example.yml")
ECE4_PLATFORMS_DIR = str(_ECE4_CACHE_BASE / "scripts/platforms")

def get_recipe_path(recipe_name):
    """Get path to recipe, checking user recipes first, then built-in.

    Search order:
    1. Absolute path (if provided)
    2. User recipes (~/.config/ece4-exp/recipes/)
    3. Built-in recipes (installed with package)
    """
    if not recipe_name:
        return None
    if not recipe_name.endswith((".yml", ".yaml")):
        recipe_name += ".yml"

    # Check if absolute path
    if os.path.isabs(recipe_name):
        return recipe_name

    # Check user recipes first
    user_recipe = USER_RECIPES_DIR / recipe_name
    if user_recipe.exists():
        return str(user_recipe)

    # Fall back to built-in recipes
    return os.path.join(RECIPES_DIR, recipe_name)

def get_platform_launchers_path(platform_name):
    """Get path to platform launchers file.

    Search order:
    1. User platforms (~/.config/ece4-exp/platforms/)
    2. Built-in platforms (installed with package)

    Args:
        platform_name: Platform name (e.g., 'bsc-marenostrum5')

    Returns:
        Path to platform YAML file
    """
    if not platform_name:
        return None
    if not platform_name.endswith((".yml", ".yaml")):
        platform_name += ".yml"

    # Check user platforms first
    user_platform = USER_PLATFORMS_DIR / platform_name
    if user_platform.exists():
        return str(user_platform)

    # Fall back to built-in platforms
    return os.path.join(PLATFORMS_DIR, platform_name)

def get_ecearth4_platform_path(platform_name):
    """Get path to platform file from ecearth4 repo.

    The platform_name might be short (e.g. 'bsc-marenostrum5') but the actual
    files have compiler suffix (e.g. 'bsc-marenostrum5-intel+openmpi.yml').
    We try to find a matching file by prefix.

    Args:
        platform_name: Platform name (e.g., 'bsc-marenostrum5', 'ecmwf-hpc2020')

    Returns:
        Path to platform YAML file, or None if not found
    """
    if not os.path.exists(ECE4_PLATFORMS_DIR):
        return None

    # Try exact match first
    exact_path = os.path.join(ECE4_PLATFORMS_DIR, f"{platform_name}.yml")
    if os.path.exists(exact_path):
        return exact_path

    # Try to find by prefix (e.g. 'bsc-marenostrum5' matches 'bsc-marenostrum5-intel+openmpi.yml')
    import glob
    matches = glob.glob(os.path.join(ECE4_PLATFORMS_DIR, f"{platform_name}*.yml"))
    if matches:
        # Return first match (alphabetically sorted for consistency)
        # Future: could add logic to prefer certain compilers (intel > gcc, etc.)
        return sorted(matches)[0]

    return None
