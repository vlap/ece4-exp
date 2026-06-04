# Bash completion for ece4-recipe.sh

_ece4_recipe_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="init-user info list generate validate save"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        generate|info)
            local flags="--platform --launcher --kind --sim-procs --recipe --repo-owner --repo-branch --dry-run"
            COMPREPLY=( $(compgen -W "${flags}" -- ${cur}) )
            ;;
        --recipe)
            local recipes=""
            if [[ -d "recipes" ]]; then
                recipes+="$(find recipes -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) -printf '%f
' 2>/dev/null) "
            fi
            if [[ -d "recipes/weekly_tests" ]]; then
                recipes+="$(find recipes/weekly_tests -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) -printf '%f
' 2>/dev/null) "
            fi
            COMPREPLY=( $(compgen -W "${recipes}" -- ${cur}) )
            ;;
        save)
            local save_flags="--recipe --expid"
            COMPREPLY=( $(compgen -W "${save_flags}" -- ${cur}) )
            ;;
        validate)
            local ymls=$(ls *.yml 2>/dev/null)
            COMPREPLY=( $(compgen -W "${ymls}" -- ${cur}) )
            ;;
        --platform)
            local platforms="bsc-marenostrum5 ecmwf-hpc2020"
            COMPREPLY=( $(compgen -W "${platforms}" -- ${cur}) )
            ;;
        --launcher)
            local launchers="slurm slurm-wrapper-taskset slurm-wrapper-hostfile slurm-hetjob"
            COMPREPLY=( $(compgen -W "${launchers}" -- ${cur}) )
            ;;
    esac
}

complete -F _ece4_recipe_completion ece4-recipe.sh
complete -F _ece4_recipe_completion ./ece4-recipe.sh
