#!/usr/bin/env python3

import argparse
from copy import deepcopy
import os
from pathlib import Path
import sys

from .yaml_util import (
    load_yaml, save_yaml_config, load_yaml_config, deep_merge,
    get_yaml, log_info, log_error, log_warn, log_yaml, COLOR_CYAN, COLOR_NC
)
from . import paths

yaml_rt = get_yaml()

# ------------------------------------------------------------------
# Semantic comparison (ignores ruamel tag/style metadata)
# ------------------------------------------------------------------

def values_equal(a, b):
    """Compare two YAML nodes semantically."""
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(values_equal(a[k], b[k]) for k in a)

    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(values_equal(x, y) for x, y in zip(a, b))

    return str(a) == str(b)


# ------------------------------------------------------------------
# Recursive overlay computation
# ------------------------------------------------------------------

def compute_overlay(base, modified):
    """Compute minimal overlay such that deep_merge(base, overlay) == modified."""
    if isinstance(base, dict) and isinstance(modified, dict):
        overlay = yaml_rt.map()

        for key in modified:
            if key not in base:
                overlay[key] = modified[key]
            else:
                diff = compute_overlay(base[key], modified[key])
                if diff is not None:
                    overlay[key] = diff

        return overlay if overlay else None

    if isinstance(base, list) and isinstance(modified, list):
        if not values_equal(base, modified):
            return modified
        return None

    if not values_equal(base, modified):
        return modified

    return None


# ------------------------------------------------------------------
# Recipe generation
# ------------------------------------------------------------------

def create_recipe_from_diff(modified_file, pristine_file, recipe_path,
                             expdef_path=None, user_recipe_name=None):
    """Extract a minimal recipe overlay from the diff between pristine and modified configs.

    Args:
        modified_file: Path to the user-edited experiment YAML.
        pristine_file: Path to the pristine copy saved at generate time.
        recipe_path:   Where to write the resulting recipe file.
        expdef_path:   Optional Autosubmit expdef file (fallback for user_recipe_name).
        user_recipe_name: Base recipe to include in the saved overlay.
    """
    modified_file = str(modified_file)
    pristine_file = str(pristine_file)

    if not os.path.exists(modified_file):
        log_error(f"Experiment file not found: {modified_file}")
        log_info("Make sure you are in the directory where the config was generated,")
        log_info("or use --config to specify its path.")
        return False

    if not os.path.exists(pristine_file):
        log_error(f"Pristine copy not found: {pristine_file}")
        log_info("Run 'ece4-exp generate' first to create the pristine copy.")
        return False

    try:
        pristine = load_yaml_config(pristine_file)
        modified = load_yaml_config(modified_file)
    except Exception as e:
        log_error(f"Failed to load experiment files: {e}")
        return False

    overlay = compute_overlay(pristine, modified)

    # Resolution order for the base recipe name:
    # 1. CLI --recipe flag
    # 2. _ece4_recipe stamp in the modified file (written at generate time)
    # 3. Autosubmit expdef.yml
    if not user_recipe_name:
        user_recipe_name = modified.get("experiment", {}).get("_ece4_recipe")
        if user_recipe_name:
            log_info(f"Using recipe from generated file: {user_recipe_name}")

    if not user_recipe_name and expdef_path and os.path.exists(expdef_path):
        try:
            expdef_conf = load_yaml(expdef_path)
            user_recipe_name = expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("USER_RECIPE")
        except Exception as e:
            log_warn(f"Failed to load {expdef_path}: {e}")

    current_recipe = None
    if user_recipe_name:
        recipe_input_path = paths.get_recipe_path(user_recipe_name)
        if recipe_input_path and os.path.exists(recipe_input_path):
            current_recipe = load_yaml_config(recipe_input_path)
        else:
            log_warn(f"Base recipe '{user_recipe_name}' not found — saving overlay only.")

    if overlay is not None:
        merged = deep_merge(deepcopy(current_recipe), deepcopy(overlay))
        Path(recipe_path).parent.mkdir(parents=True, exist_ok=True)
        save_yaml_config(recipe_path, merged, mode="ece4")

        log_info(f"Recipe saved: {COLOR_CYAN}{recipe_path}{COLOR_NC}")
        print("\n--- Saved Recipe Content ---\n")
        log_yaml(merged)
        log_info("Reuse with: ece4-exp generate <this-recipe> NODES EXPID")
        return True
    else:
        log_info("No changes detected relative to the pristine configuration.")
        if current_recipe:
            print(f"\n--- Current Recipe ({user_recipe_name}) ---\n")
            log_yaml(current_recipe)
        return True


# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate minimal recipe YAML from diff between pristine and modified experiment YAML."
    )
    parser.add_argument("--expid", required=True, help="Experiment ID (4 alphanumeric characters)")
    parser.add_argument("--config", help="Path to the edited experiment YAML (default: {expid}_experiment.yml in CWD)")
    parser.add_argument("-o", "--output", help="Output recipe path (default: ~/.config/ece4-exp/recipes/{expid}.yml)")
    parser.add_argument("--expdef", help="Path to Autosubmit expdef_EXPID.yml file")
    parser.add_argument("--recipe", help="Base recipe name to merge into the overlay")

    args = parser.parse_args()

    modified_file = args.config or f"{args.expid}_experiment.yml"
    pristine_file = paths.USER_CONFIG_DIR / f"{args.expid}_experiment_pristine.yml"

    if args.output:
        recipe_path = args.output
    else:
        paths.USER_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
        recipe_path = str(paths.USER_RECIPES_DIR / f"{args.expid}.yml")

    create_recipe_from_diff(
        modified_file=modified_file,
        pristine_file=pristine_file,
        recipe_path=recipe_path,
        expdef_path=args.expdef,
        user_recipe_name=args.recipe,
    )


if __name__ == "__main__":
    main()
