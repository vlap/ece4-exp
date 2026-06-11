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
    get_yaml, log_info, log_warn, log_error, log_yaml, COLOR_CYAN, COLOR_NC, set_quiet_mode
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
    """Execute git command safely with user-friendly error messages."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        check=False,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()

        # Provide user-friendly error messages for common access issues
        if "couldn't find remote ref" in stderr:
            branch_or_tag = args[-1] if args else "unknown"
            raise RuntimeError(
                f"Branch or tag '{branch_or_tag}' not found.\n"
                f"Check the branch/tag name is correct and you have access to it.\n"
                f"Use --repo-branch to specify a different branch (e.g., main, v4.1.6)"
            )
        elif "not found" in stderr and "repository" in stderr:
            raise RuntimeError(
                f"Cannot access EC-Earth4 repository.\n"
                f"Possible reasons:\n"
                f"  - Repository owner doesn't exist (check --repo-owner)\n"
                f"  - Repository is private and you don't have access\n"
                f"  - Network connection issue\n"
                f"Contact your EC-Earth administrator if you need access."
            )
        elif "permission" in stderr.lower():
            raise RuntimeError(
                f"Permission denied when accessing repository.\n"
                f"You may need to:\n"
                f"  - Request access to this repository\n"
                f"  - Set up SSH keys or authentication\n"
                f"  - Contact the repository administrator"
            )
        else:
            # Generic error with full git output
            raise RuntimeError(
                f"Git command failed: git {' '.join(args)}\n"
                f"{stderr}"
            )

    return result.stdout.strip()


def clone_ece4_yml_repo(
    repo_owner: str,
    repo_branch: str,
    *sparse_files: str,
    tmpd: str = None,
) -> dict:
    """
    Synchronizes EC-Earth4 repository using sparse checkout with smart caching.

    Uses ~/.config/ece4-exp/cache/ecearth4/ for persistent, shared cache.
    Intelligently switches repo_owner/branch without re-cloning.

    Args:
        repo_owner: Repository owner (e.g., 'ec-earth')
        repo_branch: Branch/tag to checkout (e.g., 'v4.1.6')
        sparse_files: Files to include in sparse checkout
        tmpd: Override cache location (for testing)

    Returns:
        dict with 'is_cached' (bool), 'commit' (str), 'switched_remote' (bool)
    """
    if not repo_owner or not repo_branch:
        raise ValueError("repo_owner and repo_branch must be provided")

    repo_url = f"https://git.smhi.se/{repo_owner}/ecearth4.git"

    # Use user cache directory (persistent across reinstalls)
    if tmpd is None:
        repo_path = paths.ECE4_CACHE_REPO
    else:
        repo_path = Path(tmpd)

    is_cached = False
    switched_remote = False

    # --- Cache Detection & Remote Handling ---
    if repo_path.exists() and (repo_path / ".git").exists():
        try:
            current_remote = _run_git(["remote", "get-url", "origin"], cwd=repo_path)

            if current_remote == repo_url:
                # Same remote - use cached repo
                is_cached = True
            else:
                # Different remote - update URL instead of deleting
                log_info(f"Switching repo from {current_remote} to {repo_url}")
                _run_git(["remote", "set-url", "origin", repo_url], cwd=repo_path)
                switched_remote = True
                is_cached = True  # Still using cached git dir
        except Exception as e:
            # Corrupted repo - remove and start fresh
            log_warn(f"Cached repo corrupted, re-initializing: {e}")
            shutil.rmtree(repo_path)
            is_cached = False

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
    # Fetch with depth 1 to keep it lightweight
    _run_git(["fetch", "--depth", "1", "origin", repo_branch], cwd=repo_path)
    _run_git(["checkout", "FETCH_HEAD"], cwd=repo_path)

    commit = _run_git(["rev-parse", "--short", "HEAD"], cwd=repo_path)

    return {
        "is_cached": is_cached,
        "commit": commit,
        "switched_remote": switched_remote,
    }

def build_cli_overrides(expid, account, walltime, description, qos=None):
    """Build configuration overrides from CLI parameters.

    Note: scratch is not a parameter - it should come from user's config file,
    not be hardcoded in every experiment.
    """
    overrides = {}

    if expid:
        if "experiment" not in overrides:
            overrides["experiment"] = {}
        overrides["experiment"]["id"] = expid

    if description:
        if "experiment" not in overrides:
            overrides["experiment"] = {}
        overrides["experiment"]["description"] = description

    if account or walltime or qos:
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
        if qos:
            overrides["job"]["slurm"]["sbatch"]["opts"]["qos"] = qos
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
                   expid=None, account=None, walltime=None, description=None, qos=None,
                   output="experiment.yml", dry_run=False, ece4_version=None):
    """Generate an experiment configuration by merging multiple configuration fragments.

    The platform file is loaded separately by the workflow, so we don't merge it here.

    Merge order:
    1. base (from git repo: experiment-config-example.yml)
    2. launcher_fragment (from local: platforms/<platform>.yml - job launch configuration)
    3. recipe (science configuration)
    4. cli_overrides (explicit user parameters)

    Note: Platform config is only used to extract cpus_per_node as a fallback if platform file doesn't have 'ppn'.
    """
    # Load base configuration from git repo (resolve path after clone)
    base = load_yaml_config(paths.get_base_config_example())

    # Platform files are NOT merged into experiment config (they're loaded separately by the workflow).
    # We only need platform_config as a fallback source for cpus_per_node if platform file doesn't have ppn.
    platform_config = {}

    # Load platform launchers (local ece4-exp specific)
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
    cli_overrides = build_cli_overrides(expid, account, walltime, description, qos)

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

    # Stamp which EC-Earth4 version this config was generated for
    if ece4_version:
        if "experiment" not in merged:
            merged["experiment"] = {}
        merged["experiment"]["_ece4_version"] = ece4_version

    if dry_run:
        print("\n--- Generated YAML (dry-run) ---\n")
        log_yaml(merged)
        return

    save_yaml_config(output, merged)

def load_user_defaults():
    """Load user defaults from ~/.config/ece4-exp/defaults.yml if it exists."""
    if paths.USER_DEFAULTS_FILE.exists():
        try:
            return load_yaml(str(paths.USER_DEFAULTS_FILE))
        except Exception as e:
            log_warn(f"Could not load user defaults from {paths.USER_DEFAULTS_FILE}: {e}")
    return {}

def main():
    parser = argparse.ArgumentParser(
        description="Generate EC-Earth4 experiment config.",
        epilog="Parameters are resolved in this order: CLI args > user config (~/.config/ece4-exp/defaults.yml) > autosubmit files (if provided)"
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
    parser.add_argument("--expid", help="Experiment ID (4 alphanumeric characters, e.g., a001, test)")
    parser.add_argument("--account", help="HPC account/project")
    parser.add_argument("--walltime", help="Walltime in hours (e.g. 48)")
    parser.add_argument("--description", help="Experiment description")

    # Output control
    parser.add_argument("-o", "--output", default=None, help="Output YAML file name (default: {expid}_experiment.yml)")
    parser.add_argument("--dry-run", action="store_true", help="Print YAML instead of writing to file")
    parser.add_argument("--quiet", action="store_true", help="Suppress colored output and prompts (for scripting)")
    parser.add_argument("--info", action="store_true", help="Only print extracted settings and exit")
    args = parser.parse_args()

    # Enable quiet mode if --quiet flag is set
    if args.quiet:
        set_quiet_mode(True)

    # Load user defaults from ~/.config/ece4-exp/defaults.yml
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
    account = args.account or user_defaults.get("account")
    qos = user_defaults.get("qos")  # qos only from user defaults, not CLI
    walltime = args.walltime or user_defaults.get("walltime")
    description = args.description or user_defaults.get("description")

    # Validate expid format (EC-Earth4 standard: exactly 4 alphanumeric characters)
    if expid:
        if not re.match(r'^[a-zA-Z0-9]{4}$', expid):
            log_error(f"Invalid expid '{expid}': Must be exactly 4 alphanumeric characters (EC-Earth4 standard)")
            log_info("Examples: a001, test, exp1, gcm4")
            sys.exit(1)

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
        log_info("Quick fix: run 'ece4-exp setup' to configure your platform and account.")
        log_info("Or provide them via CLI flags (--platform, --account, etc.)")
        sys.exit(1)

    from .yaml_util import _get_color
    cyan = _get_color(COLOR_CYAN)
    nc = _get_color(COLOR_NC)

    print(f"{cyan}============================================================{nc}")
    print(f" Experiment Configuration Settings")
    print(f"------------------------------------------------------------")
    print(f" ECE4 repo owner     : \"{cyan}{repo_owner}{nc}\"")
    print(f" ECE4 repo branch    : \"{cyan}{repo_branch}{nc}\"")
    print(f" Platform            : \"{cyan}{hpcarch}{nc}\"")
    print(f"------------------------------------------------------------")
    print(f" Experiment ID       : {cyan}{expid or '(not set)'}{nc}")
    print(f" Account             : {cyan}{account or '(not set)'}{nc}")
    print(f" Walltime (hours)    : {cyan}{walltime or '(not set)'}{nc}")
    print(f"------------------------------------------------------------")
    print(f" Processors (SIM)    : {cyan}{sim_procs}{nc}")
    print(f" Launcher kind       : {cyan}{launcher_kind}{nc}")
    print(f" Launcher type       : {cyan}{launcher_type}{nc}")
    print(f" Recipe              : {cyan}{user_recipe or '(none)'}{nc}")
    print(f"{cyan}============================================================{nc}")

    if args.info:
        sys.exit(0)

    try:
        log_info(f"ECE4 repository synchronization: owner='{repo_owner}', ref='{repo_branch}'")
        result = clone_ece4_yml_repo(
            repo_owner,
            repo_branch,
            "scripts/runtime/experiment-config-example.yml",
            # Uses user cache: ~/.config/ece4-exp/cache/ecearth4/
            # tmpd parameter removed - now uses smart default from paths.ECE4_CACHE_REPO
        )

        # Build status message
        if result.get("switched_remote"):
            status = "(switched repo)"
        elif result["is_cached"]:
            status = "(cached)"
        else:
            status = "(initialized)"

        log_info(f"Successfully synced {repo_branch} at {result['commit']} {status}.")

    except Exception as e:
        log_error(f"Failed to sync ECE4 repo:\n{e}")
        sys.exit(1)

    # Auto-generate output filename if not specified
    output_file = args.output
    if not output_file and expid:
        output_file = f"{expid}_experiment.yml"
    elif not output_file:
        output_file = "experiment.yml"

    generate_config(
        platform=hpcarch,
        launcher=launcher_type,
        launcher_kind=launcher_kind,
        sim_procs=sim_procs,
        user_recipe=user_recipe,
        expid=expid,
        account=account,
        walltime=walltime,
        description=description,
        qos=qos,
        output=output_file,
        dry_run=args.dry_run,
        ece4_version=repo_branch,
    )

    if not args.dry_run:
        # Save pristine copy for recipe extraction (always in USER_CONFIG_DIR, regardless of output path)
        pristine_name = Path(output_file).name.replace(".yml", "_pristine.yml")
        pristine_file = paths.USER_CONFIG_DIR / pristine_name
        shutil.copyfile(output_file, pristine_file)

        from .yaml_util import _get_color
        cyan = _get_color(COLOR_CYAN)
        nc = _get_color(COLOR_NC)

        log_info(f"GENERATED EXPERIMENT CONFIGURATION FILE: {cyan}{output_file}{nc}")
        log_warn("Review and make any necessary changes BEFORE running the experiment.")
        log_info(f"Tip: You can compare with the base config or validate with {cyan}ece4-exp validate {output_file}{nc}")
        print("\n")

if __name__ == "__main__":
    main()
