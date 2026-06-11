#!/usr/bin/env python3
"""
CLI entry point for ece4-exp.

This replaces the bash wrapper with a proper Python console_scripts entry point.
"""

import argparse
import os
import sys
from pathlib import Path

from . import paths
from .yaml_util import log_info, log_warn, log_error, COLOR_CYAN, COLOR_GREEN, COLOR_NC


def cmd_list(args):
    """List available recipes."""
    print(f"{COLOR_CYAN}Available Recipes:{COLOR_NC}\n")

    # User recipes (show first - they override built-in)
    user_recipes = []
    if paths.USER_RECIPES_DIR.exists():
        user_recipes = sorted(paths.USER_RECIPES_DIR.glob("*.yml")) + sorted(paths.USER_RECIPES_DIR.glob("*.yaml"))
        if user_recipes:
            print(f"{COLOR_GREEN}Your Recipes:{COLOR_NC}")
            for recipe in user_recipes:
                print(f"  - {recipe.name}")
            print()

    # Built-in recipes
    print("Built-in Recipes:")
    if paths.RECIPES_DIR.exists():
        recipes = sorted(paths.RECIPES_DIR.glob("*.yml")) + sorted(paths.RECIPES_DIR.glob("*.yaml"))
        for recipe in recipes:
            print(f"  - {recipe.name}")
    else:
        log_warn(f"Recipes directory not found: {paths.RECIPES_DIR}")

    # Locations
    print(f"\n{COLOR_GREEN}Locations:{COLOR_NC}")
    user_recipes_status = "(empty)" if not user_recipes else f"({len(user_recipes)} custom)"
    print(f"  User recipes:     {paths.USER_RECIPES_DIR} {user_recipes_status}")
    print(f"  Built-in recipes: {paths.RECIPES_DIR}")

    user_platforms = list(paths.USER_PLATFORMS_DIR.glob("*.yml")) if paths.USER_PLATFORMS_DIR.exists() else []
    user_platforms_status = "(empty)" if not user_platforms else f"({len(user_platforms)} custom)"
    print(f"  User platforms:   {paths.USER_PLATFORMS_DIR} {user_platforms_status}")
    print(f"  Built-in platforms: {paths.PLATFORMS_DIR}")

    print(f"\n{COLOR_GREEN}Usage:{COLOR_NC}")
    print(f"  ece4-exp inspect <recipe.yml> - View recipe contents")
    print(f"  ece4-exp save --expid <id>    - Save your modifications as recipe")
    print(f"  cp recipe.yml {paths.USER_RECIPES_DIR}/  - Add external recipe")
    print(f"  cp platform.yml {paths.USER_PLATFORMS_DIR}/  - Add custom platform")
    print()


def cmd_deploy(args):
    """rsync generated experiment config to the HPC runtime directory."""
    import re
    import subprocess

    expid = args.expid
    if not re.match(r'^[a-zA-Z0-9]{4}$', expid):
        log_error(f"Invalid expid '{expid}': Must be exactly 4 alphanumeric characters")
        sys.exit(1)

    # Source file
    config_file = args.config or f"{expid}_experiment.yml"
    if not Path(config_file).exists():
        log_error(f"Config file not found: {config_file}")
        log_info(f"Generate it first: ece4-exp generate RECIPE NODES {expid}")
        sys.exit(1)

    # Destination: resolve from args > defaults.yml
    host = args.host
    scratch = args.scratch
    if not host or not scratch:
        try:
            from .yaml_util import load_yaml
            defaults = load_yaml(str(paths.USER_DEFAULTS_FILE))
            host = host or defaults.get("host")
            scratch = scratch or defaults.get("scratch")
        except Exception:
            pass

    if not host:
        log_error("No host configured. Provide --host or add 'host: user@hostname' to ~/.config/ece4-exp/defaults.yml")
        sys.exit(1)
    if not scratch:
        log_error("No scratch path configured. Provide --scratch or add 'scratch: /path/to/scratch' to ~/.config/ece4-exp/defaults.yml")
        sys.exit(1)

    dest = f"{host}:{scratch}/ecearth4/scripts/runtime/"
    cmd = ["rsync", "-az", "--progress", config_file, dest]

    log_info(f"Deploying {COLOR_CYAN}{config_file}{COLOR_NC} → {COLOR_CYAN}{dest}{COLOR_NC}")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        log_error("rsync failed.")
        sys.exit(result.returncode)

    log_info(f"Done. Run the experiment with:")
    print(f"  ssh {host}")
    print(f"  cd {scratch}/ecearth4/scripts/runtime")
    print(f"  se user.yml platform.yml {Path(config_file).name} scriptlib/main.yml")


def cmd_completion(args):
    """Generate shell completion script."""
    from .completion import generate_completion

    try:
        script = generate_completion(args.shell)
        print(script)
    except ValueError as e:
        log_error(str(e))
        sys.exit(1)


def cmd_info(args):
    """Show current configuration info."""
    from .yaml_util import set_quiet_mode

    if args.quiet:
        set_quiet_mode(True)

    # Get EXPID from environment or guess
    expid = os.environ.get("EXPID", "unknown")
    if expid == "unknown":
        # Try to guess from path structure
        cwd_parts = Path.cwd().parts
        if len(cwd_parts) >= 3:
            guess = cwd_parts[-3]
            if len(guess) == 4 and guess.isalnum():
                expid = guess

    conf_path = os.environ.get("CONF_PATH", f"/esarchive/autosubmit/{expid}/conf")
    expdef_file = Path(conf_path) / f"expdef_{expid}.yml"
    jobs_file = Path(conf_path) / f"jobs_{expid}.yml"

    from .generate_experiment_config import run_generate

    run_generate(
        expdef=str(expdef_file),
        jobs=str(jobs_file),
        info=True,
        quiet=args.quiet,
    )


def cmd_setup(args):
    """Initialize user configuration."""
    log_info("Setting up ece4-exp configuration in ~/.config/ece4-exp")

    from . import init_config
    init_config.main()


def cmd_generate(args):
    """Generate experiment configuration."""
    import re
    from .yaml_util import set_quiet_mode, load_yaml_config

    # Apply quiet mode first so all subsequent log_* calls respect it
    if args.quiet:
        set_quiet_mode(True)
        os.environ["COLOR_NC"] = ""
        os.environ["COLOR_GREEN"] = ""
        os.environ["COLOR_CYAN"] = ""
        os.environ["COLOR_YELLOW"] = ""
        os.environ["COLOR_RED"] = ""

    # Merge positional and flag arguments (backward compat)
    recipe = args.recipe or getattr(args, 'recipe_flag', None)
    nodes = getattr(args, 'nodes', None)
    sim_procs = getattr(args, 'sim_procs_flag', None)
    nodes_flag = getattr(args, 'nodes_flag', None)
    expid = args.expid or getattr(args, 'expid_flag', None)

    def _nodes_to_procs(n):
        """Convert node count to processor count by reading ppn from the platform file."""
        platform = args.platform
        if not platform:
            try:
                defaults = load_yaml_config(paths.USER_DEFAULTS_FILE)
                platform = defaults.get('platform')
            except Exception:
                pass

        ppn = None
        if platform:
            platform_path = paths.get_platform_launchers_path(platform)
            if platform_path:
                try:
                    launchers = load_yaml_config(platform_path)
                    ppn = launchers.get('ppn')
                except Exception:
                    pass

        if not ppn:
            ppn = 112  # MareNostrum5 fallback
            if not platform:
                log_warn("No platform configured. Run 'ece4-exp setup' first.")
            log_info(f"Assuming {ppn} cores/node (MareNostrum5 default)")

        log_info(f"Converting {n} nodes → {n * ppn} processors ({ppn} cores/node)")
        return n * ppn

    # Determine if user provided nodes or sim_procs
    if nodes is not None:
        sim_procs = _nodes_to_procs(nodes)
    elif nodes_flag is not None:
        sim_procs = _nodes_to_procs(nodes_flag)
    elif sim_procs is None:
        sim_procs = None

    # Normalize recipe name (allow "gcm-sr" or "gcm-sr.yml")
    if recipe and not recipe.endswith(('.yml', '.yaml')):
        recipe = f"{recipe}.yml"

    # Validate expid format if provided (EC-Earth4 standard: exactly 4 alphanumeric characters)
    if expid:
        if not re.match(r'^[a-zA-Z0-9]{4}$', expid):
            log_error(f"Invalid expid '{expid}': Must be exactly 4 alphanumeric characters")
            log_info("Examples: a001, test, exp1, gcm4")
            sys.exit(1)

    # Better error messages with suggestions
    if not recipe or not sim_procs or not expid:
        missing = []
        if not recipe: missing.append("RECIPE")
        if not sim_procs: missing.append("NODES")
        if not expid: missing.append("EXPID")

        log_error(f"Missing required arguments: {', '.join(missing)}")
        print(f"\n{COLOR_GREEN}Usage:{COLOR_NC}")
        print(f"  ece4-exp generate RECIPE NODES EXPID")
        print(f"\n{COLOR_GREEN}Examples:{COLOR_NC}")
        print(f"  ece4-exp generate gcm-sr 10 a001     # 10 nodes")
        print(f"  ece4-exp generate omip-sr 2 o001     # 2 nodes")
        print(f"\n{COLOR_GREEN}What's NODES?{COLOR_NC}")
        print(f"  Just the number of compute nodes (tool calculates processors)")
        print(f"  Old style still works: --sim-procs 1120")
        print(f"\n{COLOR_GREEN}First time?{COLOR_NC}")
        print(f"  Run 'ece4-exp setup' to configure platform")
        print(f"  Run 'ece4-exp list' to see available recipes")
        sys.exit(1)

    from .generate_experiment_config import run_generate

    conf_path = os.environ.get("CONF_PATH", f"/esarchive/autosubmit/{expid}/conf")
    expdef_file = Path(conf_path) / f"expdef_{expid}.yml"
    jobs_file   = Path(conf_path) / f"jobs_{expid}.yml"

    run_generate(
        platform=args.platform,
        launcher=args.launcher,
        kind=args.kind,
        sim_procs=str(sim_procs) if sim_procs else None,
        recipe=recipe,
        repo_owner=args.repo_owner,
        repo_branch=args.repo_branch,
        expid=expid,
        account=args.account,
        walltime=str(args.walltime) if args.walltime else None,
        description=args.description,
        output=args.output,
        dry_run=args.dry_run,
        quiet=args.quiet,
        expdef=str(expdef_file) if expdef_file.exists() and jobs_file.exists() else None,
        jobs=str(jobs_file)   if expdef_file.exists() and jobs_file.exists() else None,
    )


def cmd_inspect(args):
    """View recipe contents."""
    from .yaml_util import load_yaml_config

    recipe_name = args.recipe
    recipe_path = paths.get_recipe_path(recipe_name)

    if not recipe_path or not Path(recipe_path).exists():
        log_error(f"Recipe not found: {recipe_name}")
        print(f"\n{COLOR_GREEN}Tip:{COLOR_NC} Use 'ece4-exp list' to see available recipes")
        sys.exit(1)

    print(f"{COLOR_CYAN}Recipe:{COLOR_NC} {recipe_name}")
    print(f"{COLOR_CYAN}Location:{COLOR_NC} {recipe_path}\n")

    # Display file contents
    with open(recipe_path, 'r') as f:
        print(f.read())


def cmd_validate(args):
    """Validate experiment configuration."""
    from . import validate_experiment_config as vec

    config_file = args.config_file
    if not config_file:
        # Default to EXPID_experiment.yml
        expid = os.environ.get("EXPID", "unknown")
        config_file = f"{expid}_experiment.yml"

    if not Path(config_file).exists():
        log_error(f"Configuration file not found: {config_file}")
        sys.exit(1)

    sys.argv = ["ece4-exp", config_file]
    vec.main()


def cmd_save(args):
    """Save changes as a recipe."""
    import re
    from .save_recipe_from_diff import create_recipe_from_diff

    expid = args.expid if args.expid else os.environ.get("EXPID", "")
    if not expid:
        log_error("No experiment ID. Provide --expid XXXX")
        sys.exit(1)
    if not re.match(r'^[a-zA-Z0-9]{4}$', expid):
        log_error(f"Invalid expid '{expid}': Must be exactly 4 alphanumeric characters")
        log_info("Examples: a001, test, exp1, gcm4")
        sys.exit(1)

    # Locate the experiment config: explicit --config, then CWD default
    if hasattr(args, 'config') and args.config:
        modified_file = Path(args.config)
    else:
        modified_file = Path(f"{expid}_experiment.yml")

    pristine_file = paths.USER_CONFIG_DIR / f"{expid}_experiment_pristine.yml"

    # Output recipe path
    if args.output:
        recipe_path = args.output
    else:
        paths.USER_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
        recipe_path = str(paths.USER_RECIPES_DIR / f"{expid}.yml")

    log_info(f"Saving recipe: {COLOR_CYAN}{recipe_path}{COLOR_NC}  (from expid: {expid})")

    # Autosubmit expdef fallback
    conf_path = os.environ.get("CONF_PATH", f"/esarchive/autosubmit/{expid}/conf")
    expdef_file = Path(conf_path) / f"expdef_{expid}.yml"

    ok = create_recipe_from_diff(
        modified_file=modified_file,
        pristine_file=pristine_file,
        recipe_path=recipe_path,
        expdef_path=str(expdef_file) if expdef_file.exists() else None,
        user_recipe_name=args.recipe,
    )
    if not ok:
        sys.exit(1)


def _recipe_completer(prefix, parsed_args, **kwargs):
    """Return recipe names for TAB completion."""
    recipes = []
    if paths.USER_RECIPES_DIR.exists():
        recipes.extend(p.stem for p in sorted(paths.USER_RECIPES_DIR.glob("*.yml")))
    if paths.RECIPES_DIR.exists():
        recipes.extend(p.stem for p in sorted(paths.RECIPES_DIR.glob("*.yml")))
    return [r for r in recipes if r.startswith(prefix)]


def main():
    """Main CLI entry point."""
    # Enable argcomplete for automatic completion
    try:
        import argcomplete
        ARGCOMPLETE_AVAILABLE = True
    except ImportError:
        ARGCOMPLETE_AVAILABLE = False

    from importlib.metadata import version as _pkg_version
    try:
        _version = _pkg_version("ece4-exp")
    except Exception:
        _version = "unknown"

    parser = argparse.ArgumentParser(
        prog="ece4-exp",
        description="EC-Earth4 experiment configuration tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ece4-exp setup                         # First-time configuration
  ece4-exp list                          # Show available recipes
  ece4-exp generate gcm-sr 10 a001       # Generate experiment config (10 nodes)
  ece4-exp deploy a001                   # Send config to HPC runtime directory
  ece4-exp inspect gcm-sr                # View recipe details

Getting Started:
  1. Run 'ece4-exp setup' to configure platform and account
  2. Use 'ece4-exp list' to see available experiment recipes
  3. Generate configs with 'ece4-exp generate RECIPE NODES EXPID'
  4. Deploy to HPC with 'ece4-exp deploy EXPID'

For detailed help: ece4-exp <command> --help
Documentation: https://ece4-exp.readthedocs.io
        """
    )

    parser.add_argument("--version", action="version", version=f"ece4-exp {_version}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- list ---
    parser_list = subparsers.add_parser("list", help="List recipes and platforms")
    parser_list.set_defaults(func=cmd_list)

    # --- completion (hidden, documented in README) ---
    parser_completion = subparsers.add_parser("completion", help=argparse.SUPPRESS)
    parser_completion.add_argument("shell", choices=["bash", "zsh"], help="Shell type (bash or zsh)")
    parser_completion.set_defaults(func=cmd_completion)

    # --- setup ---
    parser_setup = subparsers.add_parser("setup", help="Configure platform and account defaults")
    parser_setup.set_defaults(func=cmd_setup)

    # Backward compatibility
    parser_init = subparsers.add_parser("init-user", help=argparse.SUPPRESS)
    parser_init.set_defaults(func=cmd_setup)

    # --- generate ---
    parser_gen = subparsers.add_parser("generate",
        help="Generate experiment configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ece4-exp generate gcm-sr 10 a001                # Coupled GCM, 10 nodes, ID=a001
  ece4-exp generate omip-sr 2 o001                # Ocean-only, 2 nodes
  ece4-exp generate amip-sr 8 atm1 --walltime 72  # Atmosphere-only, 8 nodes

The second argument is NODES (not processors):
  MareNostrum5: 112 cores/node  → 10 nodes = 1120 cores
  ECMWF HPC2020: 128 cores/node → 10 nodes = 1280 cores
  Tool auto-calculates processors based on your platform.

Backward compatibility: --sim-procs still works
  ece4-exp generate gcm-sr --sim-procs 1120 --expid a001

First time? Run 'ece4-exp setup' to configure platform and account.
        """)

    # Positional arguments (NEW - nodes-first approach)
    recipe_arg = parser_gen.add_argument("recipe", nargs="?", help="Recipe name (e.g., gcm-sr, gcm-sr.yml)")
    if ARGCOMPLETE_AVAILABLE:
        recipe_arg.completer = _recipe_completer
    parser_gen.add_argument("nodes", nargs="?", type=int, help="Number of nodes (e.g., 10 for MareNostrum5)")
    parser_gen.add_argument("expid", nargs="?", help="Experiment ID (4 characters)")

    # Backward compatibility: --sim-procs still works
    parser_gen.add_argument("--recipe", dest="recipe_flag", help=argparse.SUPPRESS)
    parser_gen.add_argument("--sim-procs", type=int, dest="sim_procs_flag", help="Number of processors (alternative to nodes)")
    parser_gen.add_argument("--nodes", type=int, dest="nodes_flag", help=argparse.SUPPRESS)
    parser_gen.add_argument("--expid", dest="expid_flag", help=argparse.SUPPRESS)

    # Common options
    parser_gen.add_argument("--platform", help="HPC platform (overrides default)")
    parser_gen.add_argument("--account", help="HPC account (overrides default)")
    parser_gen.add_argument("--walltime", type=int, help="Walltime in hours")
    parser_gen.add_argument("-o", "--output", help="Output filename")
    parser_gen.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser_gen.add_argument("--quiet", action="store_true", help="Suppress colored output")

    # Advanced options (hidden from default help)
    parser_gen.add_argument("--launcher", help=argparse.SUPPRESS)
    parser_gen.add_argument("--kind", help=argparse.SUPPRESS)
    parser_gen.add_argument("--description", help=argparse.SUPPRESS)
    parser_gen.add_argument("--repo-owner", dest="repo_owner", help=argparse.SUPPRESS)
    parser_gen.add_argument("--repo-branch", dest="repo_branch", help=argparse.SUPPRESS)

    parser_gen.set_defaults(func=cmd_generate)

    # --- inspect ---
    parser_inspect = subparsers.add_parser("inspect", help="View recipe contents")
    inspect_recipe_arg = parser_inspect.add_argument("recipe", help="Recipe name (e.g., gcm-sr.yml)")
    if ARGCOMPLETE_AVAILABLE:
        inspect_recipe_arg.completer = _recipe_completer
    parser_inspect.set_defaults(func=cmd_inspect)

    # --- validate (hidden, auto-runs during generate) ---
    parser_val = subparsers.add_parser("validate", help=argparse.SUPPRESS)
    parser_val.add_argument("config_file", nargs="?", help="Path to configuration file")
    parser_val.set_defaults(func=cmd_validate)

    # --- deploy ---
    parser_deploy = subparsers.add_parser("deploy",
        help="Send experiment config to HPC runtime directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Deploy the generated config file to the EC-Earth4 runtime directory on the HPC.
Requires rsync and SSH access to the target host.

Examples:
  ece4-exp deploy a001                          # Uses host/scratch from defaults.yml
  ece4-exp deploy a001 --host user@mn1.bsc.es --scratch /gpfs/scratch/bsc32/bsc032XXX
  ece4-exp deploy a001 --config /path/to/a001_experiment.yml

Configure once in ~/.config/ece4-exp/defaults.yml:
  host: bsc032XXX@mn1.bsc.es
  scratch: /gpfs/scratch/bsc32/bsc032XXX
        """)
    parser_deploy.add_argument("expid", help="Experiment ID (4 alphanumeric characters)")
    parser_deploy.add_argument("--config", help="Path to experiment config (default: {expid}_experiment.yml in CWD)")
    parser_deploy.add_argument("--host", help="SSH host (e.g., user@mn1.bsc.es)")
    parser_deploy.add_argument("--scratch", help="Scratch directory on the HPC (e.g., /gpfs/scratch/bsc32/bsc032XXX)")
    parser_deploy.set_defaults(func=cmd_deploy)

    # --- save ---
    parser_save = subparsers.add_parser("save", help="Save changes as a recipe")
    parser_save.add_argument("--expid", required=True, help="Experiment ID (4 alphanumeric characters)")
    parser_save.add_argument("--config", help="Path to edited experiment YAML (default: {expid}_experiment.yml in CWD)")
    parser_save.add_argument("--recipe", help="Base recipe name to merge into the overlay")
    parser_save.add_argument("-o", "--output", help="Output recipe path (default: ~/.config/ece4-exp/recipes/{expid}.yml)")
    parser_save.set_defaults(func=cmd_save)

    # Enable argcomplete before parsing args
    if ARGCOMPLETE_AVAILABLE:
        argcomplete.autocomplete(parser)

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        log_error(f"Command failed: {e}")
        if "--debug" in sys.argv or os.environ.get("DEBUG"):
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
