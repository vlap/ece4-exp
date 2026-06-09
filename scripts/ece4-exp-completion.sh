# Bash completion for ece4-exp

_ece4_exp_completion() {
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
            local flags="--platform --launcher --kind --sim-procs --recipe --repo-owner --repo-branch --dry-run --quiet --expid --scratch --account --walltime --description"
            COMPREPLY=( $(compgen -W "${flags}" -- ${cur}) )
            ;;
        --recipe)
            local recipes=""
            if [[ -d "recipes" ]]; then
                recipes+="$(find recipes -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) -printf '%f
' 2>/dev/null) "
            fi
            COMPREPLY=( $(compgen -W "${recipes}" -- ${cur}) )
            ;;
        save)
            local save_flags="--recipe --expid -o"
            COMPREPLY=( $(compgen -W "${save_flags}" -- ${cur}) )
            ;;
        validate)
            local ymls=$(ls *.yml 2>/dev/null)
            COMPREPLY=( $(compgen -W "${ymls}" -- ${cur}) )
            ;;
        --platform)
            local platforms="bsc-marenostrum5 ecmwf-hpc2020 csc-mahti csc-lumi dkrz-levante"
            COMPREPLY=( $(compgen -W "${platforms}" -- ${cur}) )
            ;;
        --launcher)
            local launchers="slurm-wrapper-taskset slurm-wrapper-hostfile slurm-hetjob"
            COMPREPLY=( $(compgen -W "${launchers}" -- ${cur}) )
            ;;
        --kind)
            local kinds="auto CPLD-SR OMIP-SR AMIP-SR CCCL-SR"
            COMPREPLY=( $(compgen -W "${kinds}" -- ${cur}) )
            ;;
    esac
}

complete -F _ece4_exp_completion ece4-exp
complete -F _ece4_exp_completion ./ece4-exp
