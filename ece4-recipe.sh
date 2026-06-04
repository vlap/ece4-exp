#!/usr/bin/env bash

# ece4-recipe.sh - Tool for managing EC-Earth4 YAML configurations and recipes

set -euo pipefail

# --- Path Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YML_TOOLS_DIR="${PROJECT_ROOT}/ece4_recipe"
RECIPES_DIR="${PROJECT_ROOT}/recipes"

# --- Colors & Logging ---
export COLOR_NC='\033[0m' 
export COLOR_GREEN='\033[0;32m'
export COLOR_CYAN='\033[0;36m'
export COLOR_YELLOW='\033[1;33m'
export COLOR_RED='\033[0;31m'

function log_info()  { echo -e "${COLOR_GREEN}==>${COLOR_NC} $1"; }
function log_warn()  { echo -e "${COLOR_YELLOW}WARN:${COLOR_NC} $1"; }
function log_error() { echo -e "${COLOR_RED}ERROR:${COLOR_NC} $1"; }

# --- Dependency Check ---
function check_python_deps() {
    local missing=()
    if ! python3 -c "import ruamel.yaml" &>/dev/null; then missing+=("ruamel.yaml"); fi
    if ! python3 -c "import jsonschema" &>/dev/null; then missing+=("jsonschema"); fi
    
    if ! python3 -c "import pygments" &>/dev/null; then
        log_warn "Optional Python package 'pygments' not found. Syntax highlighting for dry-runs will be disabled."
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Required Python package(s) not found: ${missing[*]}"
        log_info "Please install them via: pip install ${missing[*]}"
        exit 1
    fi
}

# Load required modules if on a specific HPC (BSC Autosubmit node)
if [[ "${HOSTNAME:-}" == *"bscesautosubmit"* ]]; then
    module load ruamel.yaml jsonschema || true
fi

# --- Helper: Get Defaults ---
if [[ -z "${EXPID:-}" ]]; then
    GUESS_EXPID=$(basename "$(dirname "$(dirname "$PROJECT_ROOT")")" 2>/dev/null || echo "")
    if [[ "$GUESS_EXPID" =~ ^[a-z0-9]{4}$ ]]; then
        EXPID="$GUESS_EXPID"
    else
        EXPID="unknown"
    fi
fi

CONF_PATH=${CONF_PATH:-"/esarchive/autosubmit/${EXPID}/conf"}

# --- Command: List ---
function cmd_list() {
    echo -e "${COLOR_CYAN}Available Recipes:${COLOR_NC}"
    echo ""
    echo "Main Recipes:"
    if [[ -d "${RECIPES_DIR}" ]]; then
        find "${RECIPES_DIR}" -maxdepth 1 \( -name "*.yml" -o -name "*.yaml" \) -printf "  - %f\n" | sort
    else
        log_warn "Recipes directory not found: ${RECIPES_DIR}"
    fi
    
    if [[ -d "${RECIPES_DIR}/weekly_tests" ]]; then
        echo ""
        echo "Weekly Tests:"
        find "${RECIPES_DIR}/weekly_tests" -maxdepth 1 \( -name "*.yml" -o -name "*.yaml" \) -printf "  - %f\n" | sort
    fi
    echo ""
}

# --- Command: Info ---
function cmd_info() {
    check_python_deps
    local expdef_file="${CONF_PATH}/expdef_${EXPID}.yml"
    local jobs_file="${CONF_PATH}/jobs_${EXPID}.yml"

    PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}" \
    python3 -m ece4_recipe.generate-experiment-config \
      --expdef "$expdef_file" \
      --jobs "$jobs_file" \
      --info \
      "$@"
}

# --- Command: Init User ---
function cmd_init_user() {
    check_python_deps
    log_info "Initializing user configuration in ~/as4"
    PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}" \
    python3 -m ece4_recipe.init-user-conf
}

# --- Command: Generate ---
function cmd_generate() {
    check_python_deps
    local expdef_file="${CONF_PATH}/expdef_${EXPID}.yml"
    local jobs_file="${CONF_PATH}/jobs_${EXPID}.yml"
    local output_file="${EXPID}_experiment.yml"

    # If --output is provided in $@, it will override this one
    PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}" \
    python3 -m ece4_recipe.generate-experiment-config \
      --expdef "$expdef_file" \
      --jobs "$jobs_file" \
      --output "$output_file" \
      "$@"
}

# --- Command: Validate ---
function cmd_validate() {
    check_python_deps
    local config_file="${1:-${EXPID}_experiment.yml}"

    if [[ ! -f "$config_file" ]]; then
        log_error "Configuration file not found: $config_file"
        exit 1
    fi

    PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}" \
    python3 -m ece4_recipe.validate-experiment-config "$config_file"
}

# --- Command: Save ---
function cmd_save() {
    check_python_deps
    local expdef_file="${CONF_PATH}/expdef_${EXPID}.yml"
    
    # Extract output file from args if possible, otherwise use default
    local output_file=""
    local remaining_args=()
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --recipe|--expid) remaining_args+=("$1" "$2"); shift 2 ;;
            -*) remaining_args+=("$1"); shift ;;
            *) if [[ -z "$output_file" ]]; then output_file="$1"; else remaining_args+=("$1"); fi; shift ;;
        esac
    done
    
    output_file="${output_file:-${EXPID}.yml}"

    log_info "Saving recipe: ${COLOR_CYAN}$output_file${COLOR_NC} (Expid: ${EXPID})"
    
    PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}" \
    python3 -m ece4_recipe.save_recipe_from_diff \
      --expdef "$expdef_file" \
      --output "$output_file" \
      --expid "$EXPID" \
      "${remaining_args[@]}"
}

function usage() {
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Environment Variables:"
    echo "  EXPID       Experiment ID (default: guessed from path or 'unknown')"
    echo "  CONF_PATH   Path to experiment config files (default: /esarchive/autosubmit/\$EXPID/conf)"
    echo ""
    echo "Available commands:"
    echo "  init-user   Setup user-specific configuration in ~/as4"
    echo "  info        Show current experiment configuration"
    echo "  list        List all available recipes and weekly tests"
    echo "  generate    Generate experiment configuration"
    echo "  validate    Validate experiment configuration (optional: path to yml)"
    echo "  save        Save changes as a recipe (optional: recipe name)"
    echo ""
    echo "Flags for 'generate' and 'info':"
    echo "  --platform <id>      HPC Platform (e.g. bsc-marenostrum5)"
    echo "  --launcher <type>    Launcher type (e.g. slurm)"
    echo "  --kind <kind>        Launcher kind (e.g. CPLD-SR, auto)"
    echo "  --sim-procs <n>      Number of processors for SIM job"
    echo "  --recipe <name>      User recipe name"
    echo "  --repo-owner <user>  ECE4 repository owner"
    echo "  --repo-branch <ref>  ECE4 repository branch"
    echo "  --dry-run            Preview generated YAML"
    echo ""
    echo "Flags for 'save':"
    echo "  --recipe <name>      Current user recipe name (to compute overlay)"
    echo "  --expid <id>         Override experiment ID"
}

# --- Main ---
if [ $# -lt 1 ]; then
    usage
    exit 1
fi

command=$1
shift

case "$command" in
    init-user) cmd_init_user ;;
    info)      cmd_info "$@" ;;
    list)      cmd_list ;;
    generate)  cmd_generate "$@" ;;
    validate)  cmd_validate "$@" ;;
    save)      cmd_save "$@" ;;
    -h|--help) usage ;;
    *)
        log_error "Unknown command: $command"
        usage
        exit 1
        ;;
esac
