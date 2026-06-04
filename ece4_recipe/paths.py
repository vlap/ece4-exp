import os

# Base directory: ece4_recipe/
# Repo root is 1 level up
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main Directories
RECIPES_DIR = os.path.join(ROOT_DIR, "recipes")
WEEKLY_TESTS_DIR = os.path.join(RECIPES_DIR, "weekly_tests")
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external")
YML_TOOLS_DIR = os.path.join(ROOT_DIR, "ece4_recipe")
PLATFORMS_DIR = os.path.join(ROOT_DIR, "platforms")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
CONFIGS_DIR = os.path.join(ROOT_DIR, "configs")

# Specific paths
ASCONF_VARS = os.path.join(CONFIGS_DIR, "asconf_vars.yml")
COMPILATION_VARS = os.path.join(CONFIGS_DIR, "compilation.yml")
BASE_CONFIG_EXAMPLE = os.path.join(EXTERNAL_DIR, "ece4_yml_repo/scripts/runtime/experiment-config-example.yml")

def get_recipe_path(recipe_name):
    """Try to find recipe in recipes/ or recipes/weekly_tests/"""
    if not recipe_name:
        return None
    if not recipe_name.endswith((".yml", ".yaml")):
        recipe_name += ".yml"
    
    # Check if absolute path
    if os.path.isabs(recipe_name):
        return recipe_name
    
    # Check top level recipes
    top_path = os.path.join(RECIPES_DIR, recipe_name)
    if os.path.exists(top_path):
        return top_path
    
    # Check weekly tests
    weekly_path = os.path.join(WEEKLY_TESTS_DIR, recipe_name)
    if os.path.exists(weekly_path):
        return weekly_path
        
    return top_path # Default to top level if not found
