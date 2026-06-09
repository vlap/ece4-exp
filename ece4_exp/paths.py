import os
from pathlib import Path

# Base directory: ece4_exp/
# Repo root is 1 level up
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main Directories
RECIPES_DIR = os.path.join(ROOT_DIR, "recipes")
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external")
YML_TOOLS_DIR = os.path.join(ROOT_DIR, "ece4_exp")
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

# ECE4 repository paths (managed via sparse checkout)
BASE_CONFIG_EXAMPLE = os.path.join(EXTERNAL_DIR, "ece4_yml_repo/scripts/runtime/experiment-config-example.yml")
ECE4_PLATFORMS_DIR = os.path.join(EXTERNAL_DIR, "ece4_yml_repo/scripts/platforms")

# User config directory
USER_CONFIG_DIR = Path.home() / ".config" / "ece4-exp"
USER_DEFAULTS_FILE = USER_CONFIG_DIR / "defaults.yml"

def get_recipe_path(recipe_name):
    """Get path to recipe in recipes/ directory"""
    if not recipe_name:
        return None
    if not recipe_name.endswith((".yml", ".yaml")):
        recipe_name += ".yml"

    # Check if absolute path
    if os.path.isabs(recipe_name):
        return recipe_name

    # All recipes are now in recipes/ (flattened)
    return os.path.join(RECIPES_DIR, recipe_name)

def get_platform_launchers_path(platform_name):
    """Get path to platform launchers file (flattened: platforms/<name>.yml)"""
    return os.path.join(PLATFORMS_DIR, f"{platform_name}.yml")

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
