#!/usr/bin/env python3
"""
generate-experiment-config.py

Generates an experiment configuration by:
  1. Reading parameters from CLI flags or Autosubmit YAML files.
  2. Cloning/updating the base configuration from a git repository.
  3. Merging multiple YAML sources in a specific order.
"""

import argparse
import os
import sys
import re
import shutil
from copy import deepcopy
from io import StringIO
from .yaml_util import (
    load_yaml, load_yaml_config, save_yaml_config, deep_merge, 
    get_yaml, log_info, log_warn, log_error, log_yaml, COLOR_CYAN, COLOR_NC
)
from . import paths

import subprocess
from pathlib import Path

yaml_rt = get_yaml()

# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------
def dump_yaml_to_str(data):
    buf = StringIO()
    yaml_rt.dump(data, buf)
    return buf.getvalue()

def eval_nodes_expr(expr, nodes):
    """Evaluate '{{ nodes ... }}' expressions ."""
    if isinstance(expr, str):
        match = re.search(r"\{\{\s*(.+?)\s*\}\}", expr)
        if match:
            expr_inner = match.group(1)
            try:
                return int(eval(expr_inner, {"__builtins__": None}, {"nodes": nodes}))
            except Exception:
                return expr
    return expr

def apply_node_eval(struct, nodes):
    """Recursively replace '{{ nodes ... }}' expressions in dict/list structure."""
    if isinstance(struct, dict):
        for k, v in struct.items():
            struct[k] = apply_node_eval(v, nodes)
    elif isinstance(struct, list):
        for i, v in enumerate(struct):
            struct[i] = apply_node_eval(v, nodes)
    else:
        return eval_nodes_expr(struct, nodes)
    return struct

def _run_git(args, cwd=None):
    """Execute git command safely."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\n"
            f"{result.stderr.strip()}"
        )

    return result.stdout.strip()


def clone_ece4_yml_repo(
    repo_owner: str,
    repo_branch: str,
    *sparse_files: str,
    tmpd: str = "ece4_yml_repo",
) -> dict:
    """
    Synchronizes a repository using sparse checkout with incremental caching.
    Reuses the existing directory if the remote matches, performing a fast fetch instead of a clone.
    """
    if not repo_owner or not repo_branch:
        raise ValueError("repo_owner and repo_branch must be provided")

    repo_url = f"https://git.smhi.se/{repo_owner}/ecearth4.git"
    repo_path = Path(tmpd)
    is_cached = False

    # --- Cache Detection ---
    if repo_path.exists():
        try:
            current_remote = _run_git(["remote", "get-url", "origin"], cwd=repo_path)
            if current_remote == repo_url:
                is_cached = True
            else:
                shutil.rmtree(repo_path)
        except Exception:
            shutil.rmtree(repo_path)

    # --- Initialization (if not cached) ---
    if not is_cached:
        repo_path.mkdir(parents=True, exist_ok=True)
        _run_git(["init"], cwd=repo_path)
        _run_git(["remote", "add", "origin", repo_url], cwd=repo_path)
        _run_git(["sparse-checkout", "init", "--no-cone"], cwd=repo_path)
    
    # Always update sparse-checkout settings to match requested files
    if sparse_files:
        _run_git(["sparse-checkout", "set"] + list(sparse_files), cwd=repo_path)

    # --- Fast Fetch & Update ---
    # We fetch with depth 1 to keep it light
    _run_git(["fetch", "--depth", "1", "origin", repo_branch], cwd=repo_path)
    _run_git(["checkout", "FETCH_HEAD"], cwd=repo_path)
    
    commit = _run_git(["rev-parse", "--short", "HEAD"], cwd=repo_path)

    return {
        "is_cached": is_cached,
        "commit": commit,
    }

def select_launcher_fragment(launcher, launcher_kind, launchers_dict):
    """Selects fragment from platform-specific launchers.yml."""
    if launcher not in launchers_dict:
        log_error(f"Launcher '{launcher}' not found in launchers file.")
        sys.exit(1)

    plat_data = launchers_dict[launcher]

    merged = {}
    if "experiment" in launchers_dict:
        merged["experiment"] = deepcopy(launchers_dict["experiment"])
    if "oifs" in plat_data:
        merged["job"] = {"oifs": plat_data["oifs"]}

    if launcher_kind in plat_data:
        deep_merge(merged, {"job": plat_data[launcher_kind]})
    else:
        log_warn(f"launcher_kind '{launcher_kind}' not found for selected platform in launcher '{launcher}'.")

    return merged

def generate_config(platform, launcher, launcher_kind, sim_procs, user_recipe=None, output="experiment.yml", dry_run=False):
    """Generate an experiment configuration by merging multiple configuration fragments."""
    base = load_yaml_config(paths.BASE_CONFIG_EXAMPLE)
    asconf_vars = load_yaml_config(paths.ASCONF_VARS)
    launchers_dict = load_yaml_config(os.path.join(paths.PLATFORMS_DIR, f"{platform}/launchers.yml"))
    recipe = load_yaml_config(paths.get_recipe_path(user_recipe)) if user_recipe else None

    if launcher_kind == "auto":
        if not recipe:
            log_error("launcher_kind is 'auto' but no user_recipe provided. Cannot auto-detect configuration.")
            sys.exit(1)
        
        components = recipe.get("model_config", {}).get("components", [])
        oifs_grid = recipe.get("model_config", {}).get("oifs", {}).get("grid", "")
        nemo_grid = recipe.get("model_config", {}).get("nemo", {}).get("grid", "")

        components_set = set(components)

        if components_set == {"oifs", "xios", "nemo", "rnfm", "oasis"}:
            exp_type = "CPLD"
        elif components_set == {"oifs", "xios", "nemo", "rnfm", "oasis", "lpjg"}:
            exp_type = "CCCL"
        elif components_set == {"oifs", "xios", "amipfr", "oasis"}:
            exp_type = "AMIP"
        elif components_set == {"xios", "nemo"}:
            exp_type = "OMIP"
        else:
            raise ValueError(f"Unknown component configuration: {components}")
        
        resolution = "SR"
        if oifs_grid == "TCO95L91" and nemo_grid == "ORCA2L75":
            resolution = "LR"
        
        launcher_kind = f"{exp_type}-{resolution}"

    ppn = launchers_dict.get("ppn")
    if not ppn:
        log_error(f"Processors per node (ppn) not found for HPCARCH: {platform} in its launchers.yml.")
        sys.exit(1)
    
    sim_procs = int(sim_procs)
    nodes = sim_procs // ppn

    launcher_fragment = select_launcher_fragment(launcher, launcher_kind, launchers_dict)

    if nodes:
        apply_node_eval(launcher_fragment, nodes)

    merged = deep_merge(deepcopy(base), deepcopy(asconf_vars))
    merged["job"]["launch"]["method"] = launcher
    merged = deep_merge(merged, deepcopy(launcher_fragment))
    if user_recipe:
        merged = deep_merge(merged, deepcopy(recipe))

    if dry_run:
        print("\n--- Generated YAML (dry-run) ---\n")
        log_yaml(merged)
        return

    save_yaml_config(output, merged)

def main():
    parser = argparse.ArgumentParser(description="Generate EC-Earth4 experiment config.")
    parser.add_argument("--expdef", help="Path to expdef_EXPID.yml file")
    parser.add_argument("--jobs", help="Path to jobs_EXPID.yml file")
    parser.add_argument("--platform", help="HPC Platform (e.g. bsc-marenostrum5)")
    parser.add_argument("--launcher", help="Launcher type (e.g. slurm)")
    parser.add_argument("--kind", help="Launcher kind (e.g. CPLD-SR, auto)")
    parser.add_argument("--sim-procs", help="Number of processors for SIM job")
    parser.add_argument("--recipe", help="User recipe name")
    parser.add_argument("--repo-owner", help="ECE4 repository owner")
    parser.add_argument("--repo-branch", help="ECE4 repository branch")
    parser.add_argument("-o", "--output", default="experiment.yml", help="Output YAML file name")
    parser.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing to file")
    parser.add_argument("--info", action="store_true", help="Only print extracted settings and exit")
    args = parser.parse_args()

    expdef_conf = {}
    jobs_conf = {}

    if args.expdef and os.path.exists(args.expdef):
        expdef_conf = load_yaml(args.expdef)
    if args.jobs and os.path.exists(args.jobs):
        jobs_conf = load_yaml(args.jobs)

    # Resolution order: 1. CLI flag, 2. YAML file, 3. Default
    hpcarch = args.platform or expdef_conf.get("DEFAULT", {}).get("HPCARCH")
    repo_owner = args.repo_owner or expdef_conf.get("GIT", {}).get("SOURCES_REPO")
    repo_branch = args.repo_branch or expdef_conf.get("GIT", {}).get("SOURCES_BRANCH")
    launcher_kind = args.kind or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("LAUNCHER_KIND")
    launcher_type = args.launcher or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("LAUNCHER_TYPE")
    user_recipe = args.recipe or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("USER_RECIPE")
    
    if user_recipe and not user_recipe.endswith((".yml", ".yaml")):
        user_recipe += ".yml"
    
    sim_procs = args.sim_procs or jobs_conf.get("JOBS", {}).get("SIM", {}).get("PROCESSORS")

    # Final validation
    missing = []
    if not hpcarch: missing.append("platform")
    if not launcher_type: missing.append("launcher")
    if not launcher_kind: missing.append("kind")
    if not sim_procs: missing.append("sim-procs")
    if not repo_owner: missing.append("repo-owner")
    if not repo_branch: missing.append("repo-branch")

    if missing:
        log_error(f"Missing required parameters: {', '.join(missing)}")
        log_info("Provide them via CLI flags or Autosubmit YAML files (--expdef, --jobs).")
        sys.exit(1)

    print(f"{COLOR_CYAN}============================================================{COLOR_NC}")
    print(f" Experiment Configuration Settings")
    print(f"------------------------------------------------------------")
    print(f" ECE4 repo owner     : \"{COLOR_CYAN}{repo_owner}{COLOR_NC}\"")
    print(f" ECE4 repo branch    : \"{COLOR_CYAN}{repo_branch}{COLOR_NC}\"")
    print(f" hpcarch             : \"{COLOR_CYAN}{hpcarch}{COLOR_NC}\"")
    print(f"------------------------------------------------------------")
    print(f" Processors used in SIM : {COLOR_CYAN}{sim_procs}{COLOR_NC}")
    print(f"------------------------------------------------------------")
    print(f" Launcher kind   : {COLOR_CYAN}{launcher_kind}{COLOR_NC}")
    print(f" Launcher type   : {COLOR_CYAN}{launcher_type}{COLOR_NC}")
    print(f" User recipe     : {COLOR_CYAN}{user_recipe}{COLOR_NC}")
    print(f"{COLOR_CYAN}============================================================{COLOR_NC}")

    if args.info:
        sys.exit(0)

    try:
        log_info(f"ECE4 repository synchronization: owner='{repo_owner}', ref='{repo_branch}'")
        result = clone_ece4_yml_repo(
            repo_owner,
            repo_branch,
            "scripts/runtime/experiment-config-example.yml",
            tmpd=os.path.join(paths.EXTERNAL_DIR, "ece4_yml_repo"),
        )
        status = "(cached)" if result["is_cached"] else "(fresh clone)"
        log_info(f"Successfully synced {repo_branch} at {result['commit']} {status}.")

    except Exception as e:
        log_error(f"Failed to sync ECE4 repo:\n{e}")
        sys.exit(1)

    generate_config(
        platform=hpcarch,
        launcher=launcher_type,
        launcher_kind=launcher_kind,
        sim_procs=sim_procs,
        user_recipe=user_recipe,
        output=args.output,
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        shutil.copyfile(args.output, os.path.join(paths.YML_TOOLS_DIR, args.output.replace(".yml", "_pristine.yml")))

        log_info(f"GENERATED EXPERIMENT CONFIGURATION FILE: {COLOR_CYAN}{args.output}{COLOR_NC}")
        log_warn("Review and make any necessary changes BEFORE running the experiment.")
        log_info(f"For example, run: {COLOR_CYAN}meld {args.output} {paths.BASE_CONFIG_EXAMPLE}{COLOR_NC}")
        print("\n")

if __name__ == "__main__":
    main()
