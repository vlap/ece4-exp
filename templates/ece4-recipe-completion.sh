# Bash completion for ece4-recipe.sh
# To use: source this file or add 'source path/to/ece4-recipe-completion.sh' to your .bashrc

_ece4_recipe_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Subcommands
    opts="init-user info list generate validate save push"

    # Command suggestions
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    # Argument suggestions
    case "${prev}" in
        generate)
            COMPREPLY=( $(compgen -W "--dry-run" -- ${cur}) )
            ;;
        save|push)
            # Find recipes in recipes/ folder if it exists
            if [[ -d "recipes" ]]; then
                local recipes=$(find recipes -name "*.yml" -printf "%f\n" 2>/dev/null)
                COMPREPLY=( $(compgen -W "${recipes}" -- ${cur}) )
            fi
            ;;
        validate)
            # Suggest current experiment yml files
            local ymls=$(ls *.yml 2>/dev/null)
            COMPREPLY=( $(compgen -W "${ymls}" -- ${cur}) )
            ;;
    esac
}

complete -F _ece4_recipe_completion ece4-recipe.sh
complete -F _ece4_recipe_completion ./ece4-recipe.sh
