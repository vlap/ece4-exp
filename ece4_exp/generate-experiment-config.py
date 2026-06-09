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
    load_yaml, load_yaml_config, load_platform_yaml, save_yaml_config, deep_merge,
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

def build_cli_overrides(expid, scratch, account, walltime, description):
    """Build configuration overrides from CLI parameters."""
    overrides = {}

    if scratch:
        overrides["scratch"] = scratch

    if expid:
        if "experiment" not in overrides:
            overrides["experiment"] = {}
        overrides["experiment"]["id"] = expid

    if description:
        if "experiment" not in overrides:
            overrides["experiment"] = {}
        overrides["experiment"]["description"] = description

    if account or walltime:
        if "job" not in overrides:
            overrides["job"] = {}
        if "slurm" not in overrides["job"]:
            overrides["job"]["slurm"] = {}
        if "sbatch" not in overrides["job"]["slurm"]:
            overrides["job"]["slurm"]["sbatch"] = {}
        if "opts" not in overrides["job"]["slurm"]["sbatch"]:
            overrides["job"]["slurm"]["sbatch"]["opts"] = {}

        if account:
            overrides["job"]["slurm"]["sbatch"]["opts"]["account"] = account
        if walltime:
            # Convert hours to HH:MM:SS format
            hours = int(walltime)
            overrides["job"]["slurm"]["sbatch"]["opts"]["time"] = f"{hours:02d}:00:00"

    return overrides

def select_launcher_fragment(launcher, launcher_kind, launchers_dict):
    """Selects fragment from platform-specific platform file."""
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

def generate_config(platform, launcher, launcher_kind, sim_procs, user_recipe=None,
                   expid=None, scratch=None, account=None, walltime=None, description=None,
                   output="experiment.yml", dry_run=False):
    """Generate an experiment configuration by merging multiple configuration fragments.

    The platform file is loaded separately by the workflow, so we don't merge it here.

    Merge order:
    1. base (from git repo: experiment-config-example.yml)
    2. launcher_fragment (from local: platforms/<platform>.yml - job launch configuration)
    3. recipe (science configuration)
    4. cli_overrides (explicit user parameters)

    Note: Platform config is only used to extract cpus_per_node as a fallback if platform file doesn't have 'ppn'.
    """
    # Load base configuration from git repo
    base = load_yaml_config(paths.BASE_CONFIG_EXAMPLE)

    # Platform files are NOT merged into experiment config (they're loaded separately by the workflow).
    # We only need platform_config as a fallback source for cpus_per_node if platform file doesn't have ppn.
    platform_config = {}

    # Load platform launchers (local ece4-recipe specific)
    launchers_dict = load_yaml_config(paths.get_platform_launchers_path(platform))

    # Load user recipe if specified
    recipe = load_yaml_config(paths.get_recipe_path(user_recipe)) if user_recipe else None

    # Auto-detect launcher kind if needed
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

    # Calculate nodes from sim_procs
    # Get ppn (processors per node) from platform file
    ppn = launchers_dict.get("ppn")
    if not ppn and platform_config:
        # Fallback: check ecearth4 platform format
        ppn = platform_config.get("platform", {}).get("cpus_per_node")

    if not ppn:
        log_error(f"Processors per node (ppn/cpus_per_node) not found for platform: {platform}")
        log_info(f"Expected 'ppn' in platforms/{platform}.yml")
        sys.exit(1)

    sim_procs = int(sim_procs)
    nodes = sim_procs // ppn

    # Select and configure launcher fragment
    launcher_fragment = select_launcher_fragment(launcher, launcher_kind, launchers_dict)
    if nodes:
        apply_node_eval(launcher_fragment, nodes)

    # Build CLI overrides (NEW: explicit user parameters)
    cli_overrides = build_cli_overrides(expid, scratch, account, walltime, description)

    # NOTE: We do NOT merge platform_config into the experiment config!
    # The platform file is loaded separately by the workflow as:
    #   se my-user-config.yml my-platform-config.yml my-experiment-config.yml scriptlib/main.yml
    # We only used platform_config to extract cpus_per_node for node calculation above.

    # Merge layers: base < launcher < recipe < cli_overrides
    merged = deepcopy(base)
    merged["job"]["launch"]["method"] = launcher
    merged = deep_merge(merged, deepcopy(launcher_fragment))
    if user_recipe:
        merged = deep_merge(merged, deepcopy(recipe))
    merged = deep_merge(merged, cli_overrides)

    if dry_run:
        print("\n--- Generated YAML (dry-run) ---\n")
        log_yaml(merged)
        return

    save_yaml_config(output, merged)

def load_user_defaults():
    """Load user defaults from ~/.config/ece4-recipe/defaults.yml if it exists."""
    if paths.USER_DEFAULTS_FILE.exists():
        try:
            return load_yaml(str(paths.USER_DEFAULTS_FILE))
        except Exception as e:
            log_warn(f"Could not load user defaults from {paths.USER_DEFAULTS_FILE}: {e}")
    return {}

def main():
    parser = argparse.ArgumentParser(
        description="Generate EC-Earth4 experiment config.",
        epilog="Parameters are resolved in this order: CLI args > user config (~/.config/ece4-recipe/defaults.yml) > autosubmit files (if provided)"
    )
    # Autosubmit compatibility
    parser.add_argument("--expdef", help="Path to expdef_EXPID.yml file (autosubmit mode)")
    parser.add_argument("--jobs", help="Path to jobs_EXPID.yml file (autosubmit mode)")

    # Core parameters
    parser.add_argument("--platform", help="HPC Platform (e.g. bsc-marenostrum5)")
    parser.add_argument("--launcher", help="Launcher type (e.g. slurm-wrapper-taskset)")
    parser.add_argument("--kind", help="Launcher kind (e.g. CPLD-SR, auto)")
    parser.add_argument("--sim-procs", help="Number of processors for SIM job")
    parser.add_argument("--recipe", help="User recipe name (e.g. gcm-sr.yml)")
    parser.add_argument("--repo-owner", help="ECE4 repository owner")
    parser.add_argument("--repo-branch", help="ECE4 repository branch")

    # User-specific parameters (NEW)
    parser.add_argument("--expid", help="Experiment ID")
    parser.add_argument("--scratch", help="Scratch directory path")
    parser.add_argument("--account", help="HPC account/project")
    parser.add_argument("--walltime", help="Walltime in hours (e.g. 48)")
    parser.add_argument("--description", help="Experiment description")

    # Output control
    parser.add_argument("-o", "--output", default="experiment.yml", help="Output YAML file name")
    parser.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing to file")
    parser.add_argument("--info", action="store_true", help="Only print extracted settings and exit")
    args = parser.parse_args()

    # Load user defaults from ~/.config/ece4-recipe/defaults.yml
    user_defaults = load_user_defaults()

    # Load autosubmit files if provided (backward compatibility)
    expdef_conf = {}
    jobs_conf = {}

    if args.expdef and os.path.exists(args.expdef):
        expdef_conf = load_yaml(args.expdef)
    if args.jobs and os.path.exists(args.jobs):
        jobs_conf = load_yaml(args.jobs)

    # Resolution order: 1. CLI args, 2. User defaults, 3. Autosubmit files, 4. Error if still missing
    hpcarch = args.platform or user_defaults.get("platform") or expdef_conf.get("DEFAULT", {}).get("HPCARCH")
    repo_owner = args.repo_owner or user_defaults.get("repo_owner") or expdef_conf.get("GIT", {}).get("SOURCES_REPO")
    repo_branch = args.repo_branch or user_defaults.get("repo_branch") or expdef_conf.get("GIT", {}).get("SOURCES_BRANCH")
    launcher_kind = args.kind or user_defaults.get("kind") or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("LAUNCHER_KIND") or "auto"
    launcher_type = args.launcher or user_defaults.get("launcher") or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("LAUNCHER_TYPE")
    user_recipe = args.recipe or user_defaults.get("recipe") or expdef_conf.get("EXPERIMENT", {}).get("CONFIGURATION", {}).get("USER_RECIPE")
    sim_procs = args.sim_procs or user_defaults.get("sim_procs") or jobs_conf.get("JOBS", {}).get("SIM", {}).get("PROCESSORS")

    # User-specific parameters (NEW)
    expid = args.expid or user_defaults.get("expid")
    scratch = args.scratch or user_defaults.get("scratch")
    account = args.account or user_defaults.get("account")
    walltime = args.walltime or user_defaults.get("walltime")
    description = args.description or user_defaults.get("description")

    if user_recipe and not user_recipe.endswith((".yml", ".yaml")):
        user_recipe += ".yml"

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
        log_info("Provide them via:")
        log_info("  1. CLI flags (--platform, --launcher, etc.)")
        log_info("  2. User config: ~/.config/ece4-recipe/defaults.yml")
        log_info("  3. Autosubmit files: --expdef, --jobs (if using autosubmit)")
        sys.exit(1)

    print(f"{COLOR_CYAN}============================================================{COLOR_NC}")
    print(f" Experiment Configuration Settings")
    print(f"------------------------------------------------------------")
    print(f" ECE4 repo owner     : \"{COLOR_CYAN}{repo_owner}{COLOR_NC}\"")
    print(f" ECE4 repo branch    : \"{COLOR_CYAN}{repo_branch}{COLOR_NC}\"")
    print(f" Platform            : \"{COLOR_CYAN}{hpcarch}{COLOR_NC}\"")
    print(f"------------------------------------------------------------")
    print(f" Experiment ID       : {COLOR_CYAN}{expid or '(not set)'}{COLOR_NC}")
    print(f" Scratch dir         : {COLOR_CYAN}{scratch or '(not set)'}{COLOR_NC}")
    print(f" Account             : {COLOR_CYAN}{account or '(not set)'}{COLOR_NC}")
    print(f" Walltime (hours)    : {COLOR_CYAN}{walltime or '(not set)'}{COLOR_NC}")
    print(f"------------------------------------------------------------")
    print(f" Processors (SIM)    : {COLOR_CYAN}{sim_procs}{COLOR_NC}")
    print(f" Launcher kind       : {COLOR_CYAN}{launcher_kind}{COLOR_NC}")
    print(f" Launcher type       : {COLOR_CYAN}{launcher_type}{COLOR_NC}")
    print(f" Recipe              : {COLOR_CYAN}{user_recipe or '(none)'}{COLOR_NC}")
    print(f"{COLOR_CYAN}============================================================{COLOR_NC}")

    if args.info:
        sys.exit(0)

    try:
        log_info(f"ECE4 repository synchronization: owner='{repo_owner}', ref='{repo_branch}'")
        result = clone_ece4_yml_repo(
            repo_owner,
            repo_branch,
            "scripts/runtime/experiment-config-example.yml",
            # Note: Platform files are loaded separately by the workflow, we only need the base config
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
        expid=expid,
        scratch=scratch,
        account=account,
        walltime=walltime,
        description=description,
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
