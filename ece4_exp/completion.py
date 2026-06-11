#!/usr/bin/env python3
"""
Shell completion support for ece4-exp.

Generates completion scripts for bash and zsh.
"""

BASH_COMPLETION = """
# Bash completion for ece4-exp
# Source this file or add to ~/.bashrc:
#   eval "$(ece4-exp completion bash)"

_ece4_exp_completion() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Available commands
    commands="list info setup init-user generate inspect validate save completion"

    # Command-specific options
    generate_opts="--recipe --sim-procs --expid --platform --launcher --kind --account --walltime --description --repo-owner --repo-branch --output --dry-run --quiet"
    validate_opts=""
    save_opts="--expid --recipe --output"

    # If we're completing the first argument (command)
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    # Get the command
    local command="${COMP_WORDS[1]}"

    # Command-specific completions
    case "${command}" in
        generate)
            # Positional arg 1: recipe (without --recipe flag)
            if [ $COMP_CWORD -eq 2 ] && [[ ! "${cur}" == -* ]]; then
                local recipes=$(ls ~/.config/ece4-exp/recipes/*.yml 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/.yml$//')
                COMPREPLY=( $(compgen -W "${recipes} gcm-sr omip-sr amip-sr ccycle-sr" -- ${cur}) )
                return 0
            fi
            # Positional arg 2: procs (just show common values)
            if [ $COMP_CWORD -eq 3 ] && [[ ! "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "224 448 896 1120 2240 4480" -- ${cur}) )
                return 0
            fi
            # Positional arg 3: expid (no completion, user types)
            if [ $COMP_CWORD -eq 4 ] && [[ ! "${cur}" == -* ]]; then
                return 0
            fi
            # Flag-based completion (old syntax still works)
            case "${prev}" in
                --recipe)
                    local recipes=$(ls ~/.config/ece4-exp/recipes/*.yml 2>/dev/null | xargs -n1 basename 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${recipes} gcm-sr.yml omip-sr.yml amip-sr.yml ccycle-sr.yml" -- ${cur}) )
                    return 0
                    ;;
                --platform)
                    COMPREPLY=( $(compgen -W "bsc-marenostrum5 ecmwf-hpc2020" -- ${cur}) )
                    return 0
                    ;;
                --launcher)
                    COMPREPLY=( $(compgen -W "slurm-wrapper-taskset slurm-wrapper-hostfile slurm-hetjob" -- ${cur}) )
                    return 0
                    ;;
                --kind)
                    COMPREPLY=( $(compgen -W "auto CPLD-SR OMIP-SR AMIP-SR CCCL-SR" -- ${cur}) )
                    return 0
                    ;;
                --repo-owner)
                    COMPREPLY=( $(compgen -W "ec-earth" -- ${cur}) )
                    return 0
                    ;;
                --repo-branch)
                    COMPREPLY=( $(compgen -W "main v4.1.8 v4.1.6 v4.2.0" -- ${cur}) )
                    return 0
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "${generate_opts}" -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
        completion)
            COMPREPLY=( $(compgen -W "bash zsh" -- ${cur}) )
            return 0
            ;;
        inspect)
            # Complete recipe names (with or without .yml)
            if [ $COMP_CWORD -eq 2 ]; then
                local recipes=$(ls ~/.config/ece4-exp/recipes/*.yml 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/.yml$//')
                COMPREPLY=( $(compgen -W "${recipes} gcm-sr omip-sr amip-sr ccycle-sr" -- ${cur}) )
            fi
            return 0
            ;;
        validate)
            # Complete .yml files in current directory
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -f -X '!*.yml' -- ${cur}) )
            fi
            return 0
            ;;
        save)
            case "${prev}" in
                --recipe)
                    local recipes=$(ls ~/.config/ece4-exp/recipes/*.yml 2>/dev/null | xargs -n1 basename 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${recipes} gcm-sr.yml omip-sr.yml amip-sr.yml ccycle-sr.yml" -- ${cur}) )
                    return 0
                    ;;
                *)
                    COMPREPLY=( $(compgen -W "${save_opts}" -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
    esac
}

complete -F _ece4_exp_completion ece4-exp
"""

ZSH_COMPLETION = """
#compdef ece4-exp

# Zsh completion for ece4-exp
# Add to ~/.zshrc:
#   eval "$(ece4-exp completion zsh)"

_ece4_exp() {
    local -a commands
    commands=(
        'list:List available recipes'
        'info:Show current configuration info'
        'setup:Initialize user configuration'
        'init-user:Initialize user configuration (alias)'
        'generate:Generate experiment configuration'
        'inspect:View recipe contents'
        'validate:Validate experiment configuration'
        'save:Save changes as a recipe'
        'completion:Generate shell completion script'
    )

    local -a generate_opts
    generate_opts=(
        '--recipe[Recipe name]:recipe:_ece4_exp_recipes'
        '--sim-procs[Number of processors]:procs:'
        '--expid[Experiment ID (4 chars)]:expid:'
        '--platform[HPC platform]:platform:(bsc-marenostrum5 ecmwf-hpc2020)'
        '--launcher[Launcher type]:launcher:(slurm-wrapper-taskset slurm-wrapper-hostfile slurm-hetjob)'
        '--kind[Launcher kind]:kind:(auto CPLD-SR OMIP-SR AMIP-SR CCCL-SR)'
        '--account[HPC account]:account:'
        '--walltime[Walltime in hours]:hours:'
        '--description[Description]:description:'
        '--repo-owner[Repository owner]:owner:(ec-earth)'
        '--repo-branch[Repository branch]:branch:(main v4.1.8 v4.1.6 v4.2.0)'
        '(-o --output)'{-o,--output}'[Output file]:file:_files'
        '--dry-run[Preview without writing]'
        '--quiet[Suppress colored output]'
    )

    _arguments -C \
        '1:command:->command' \
        '*::arg:->args'

    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                generate)
                    _arguments $generate_opts
                    ;;
                inspect)
                    _arguments '1:recipe:_ece4_exp_recipes'
                    ;;
                validate)
                    _arguments '1:config file:_files -g "*.yml"'
                    ;;
                save)
                    _arguments \
                        '--expid[Experiment ID]:expid:' \
                        '--recipe[Base recipe]:recipe:_ece4_exp_recipes' \
                        '(-o --output)'{-o,--output}'[Output file]:file:_files'
                    ;;
            esac
            ;;
    esac
}

_ece4_exp_recipes() {
    local -a recipes
    recipes=(
        gcm-sr.yml:'Coupled GCM'
        omip-sr.yml:'Ocean-only'
        amip-sr.yml:'Atmosphere-only'
        ccycle-sr.yml:'Carbon cycle'
    )
    # Add user recipes
    if [ -d ~/.config/ece4-exp/recipes ]; then
        for f in ~/.config/ece4-exp/recipes/*.yml; do
            if [ -f "$f" ]; then
                recipes+=("$(basename $f):User recipe")
            fi
        done
    fi
    _describe 'recipe' recipes
}

_ece4_exp "$@"
"""


def generate_completion(shell):
    """Generate completion script for specified shell."""
    if shell == "bash":
        return BASH_COMPLETION
    elif shell == "zsh":
        return ZSH_COMPLETION
    else:
        raise ValueError(f"Unsupported shell: {shell}. Use 'bash' or 'zsh'.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(generate_completion(sys.argv[1]))
    else:
        print("Usage: ece4-exp completion [bash|zsh]")
