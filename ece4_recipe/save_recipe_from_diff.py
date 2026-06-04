#!/usr/bin/env python3

import argparse
from copy import deepcopy
import os
from pathlib import Path
import sys

# Ensure YML_TOOLS_DIR is in path for imports
# sys.path.append(...) handled by package structure

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
    """Compute minimal overlay such that: deep_merge(base, overlay) == modified"""
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

def create_recipe_from_diff(expid: str, expdef_path, recipe_path, user_recipe_name=None):
    
    modified_file = f"{expid}_experiment.yml"
    pristine_file = os.path.join(paths.YML_TOOLS_DIR, f"{expid}_experiment_pristine.yml")

    if not os.path.exists(modified_file):
        log_error(f"Modified experiment file not found: {modified_file}")
        return
    
    if not os.path.exists(pristine_file):
        log_error(f"Pristine experiment file not found: {pristine_file}")
        log_info("Ensure you have run 'generate' first to create the pristine copy.")
        return

    try:
        pristine = load_yaml_config(pristine_file)
        modified = load_yaml_config(modified_file)
    except Exception as e:
        log_error(f"Failed to load experiment files: {e}")
        return

    overlay = compute_overlay(pristine, modified)

    # Resolution order for user_recipe_name: 1. CLI flag, 2. expdef.yml
    if not user_recipe_name and expdef_path and os.path.exists(expdef_path):
        try:
            expdef_conf = load_yaml(expdef_path)
            user_recipe_name = expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("USER_RECIPE")
        except Exception as e:
            log_warn(f"Failed to load {expdef_path}: {e}")

    current_recipe = None
    if user_recipe_name:
        recipe_input_path = paths.get_recipe_path(user_recipe_name)
        if os.path.exists(recipe_input_path):
            current_recipe = load_yaml_config(recipe_input_path)
        else:
            log_warn(f"Current user recipe '{user_recipe_name}' not found at {recipe_input_path}")

    if overlay is not None:
        merged = deep_merge(deepcopy(current_recipe), deepcopy(overlay))
        save_yaml_config(recipe_path, merged, mode="ece4")

        log_info(f"Recipe generated and saved: {COLOR_CYAN}{recipe_path}{COLOR_NC}")
        print("\n--- Saved Recipe Content ---\n")
        log_yaml(merged)
        log_info("Contains base recipe and user modifications.")
        log_info("Reusable via EXPERIMENT.CONFIGURATION.USER_RECIPE.")
    else:
        log_info("No changes detected relative to pristine configuration.")
        if current_recipe:
            print(f"\n--- Current Recipe ({user_recipe_name}) ---\n")
            log_yaml(current_recipe)
        else:
            log_info("No user recipe currently active.")

# ------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate minimal recipe YAML from diff between pristine and user-modified experiment YAML."
    )

    default_expid = Path(paths.ROOT_DIR).name
    parser.add_argument("--expid", default=default_expid, help=f"Experiment ID (default: {default_expid})")
    parser.add_argument("-o", "--output", help="Recipe file name (default: <expid>.yml)")
    parser.add_argument("--expdef", help="Path to expdef_EXPID.yml file")
    parser.add_argument("--recipe", help="Current user recipe name")

    args = parser.parse_args()
    
    new_recipe_file_name = args.output if args.output else f"{args.expid}.yml"
    new_recipe_path = os.path.join(paths.RECIPES_DIR, new_recipe_file_name)

    create_recipe_from_diff(args.expid, args.expdef, new_recipe_path, user_recipe_name=args.recipe)
