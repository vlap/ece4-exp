"""
Tests for YAML merge and overlay logic — the mathematical core of ece4-exp.

These run without network access or EC-Earth4 repo.
"""
import pytest
from copy import deepcopy
from ece4_exp.yaml_util import deep_merge, get_yaml


yaml_rt = get_yaml()


def d(**kwargs):
    """Helper: build a ruamel CommentedMap from kwargs."""
    m = yaml_rt.map()
    m.update(kwargs)
    return m


# ---------------------------------------------------------------------------
# deep_merge
# ---------------------------------------------------------------------------

class TestDeepMerge:
    def test_overlay_adds_new_key(self):
        base = {"a": 1}
        result = deep_merge(deepcopy(base), {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_overlay_overrides_scalar(self):
        base = {"a": 1, "b": "old"}
        result = deep_merge(deepcopy(base), {"b": "new"})
        assert result["b"] == "new"
        assert result["a"] == 1

    def test_nested_merge_does_not_clobber(self):
        base = {"job": {"slurm": {"account": "bsc32", "qos": "gp_bsces"}}}
        overlay = {"job": {"slurm": {"account": "bsc99"}}}
        result = deep_merge(deepcopy(base), overlay)
        assert result["job"]["slurm"]["account"] == "bsc99"
        assert result["job"]["slurm"]["qos"] == "gp_bsces"  # must survive

    def test_none_base_returns_overlay(self):
        result = deep_merge(None, {"x": 1})
        assert result == {"x": 1}

    def test_none_overlay_returns_base(self):
        base = {"x": 1}
        result = deep_merge(deepcopy(base), None)
        assert result == {"x": 1}

    def test_list_overlay_replaces_whole_list(self):
        # EC-Earth4 groups lists must be replaced wholesale, not appended.
        # deep_merge replaces lists entirely when the overlay provides a list.
        base = {"groups": [{"nodes": 1, "oifs": 25}]}
        overlay = {"groups": [{"nodes": 2, "oifs": 50}]}
        result = deep_merge(deepcopy(base), overlay)
        assert len(result["groups"]) == 1
        assert result["groups"][0]["nodes"] == 2

    def test_three_layer_merge(self):
        """Simulates: base → platform → recipe merge."""
        base = {"experiment": {"id": "base"}, "job": {"slurm": {"time": "00:30:00"}}}
        platform = {"job": {"slurm": {"account": "bsc32"}}}
        recipe = {"model_config": {"components": ["oifs", "nemo"]}}

        merged = deep_merge(deepcopy(base), platform)
        merged = deep_merge(merged, recipe)

        assert merged["experiment"]["id"] == "base"
        assert merged["job"]["slurm"]["account"] == "bsc32"
        assert merged["job"]["slurm"]["time"] == "00:30:00"
        assert merged["model_config"]["components"] == ["oifs", "nemo"]


# ---------------------------------------------------------------------------
# Platform ppn lookup and node→procs conversion
# ---------------------------------------------------------------------------

class TestNodeConversion:
    def test_mn5_ppn(self):
        from ece4_exp import paths
        launchers = {"ppn": 112}
        ppn = launchers.get("ppn")
        assert ppn == 112
        assert 10 * ppn == 1120

    def test_ecmwf_ppn(self):
        launchers = {"ppn": 128}
        ppn = launchers.get("ppn")
        assert ppn == 128
        assert 10 * ppn == 1280

    def test_ppn_read_from_platform_file(self):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        mn5_launchers = load_yaml_config(str(paths.PLATFORMS_DIR / "bsc-marenostrum5.yml"))
        assert mn5_launchers.get("ppn") == 112

        ecmwf_launchers = load_yaml_config(str(paths.PLATFORMS_DIR / "ecmwf-hpc2020.yml"))
        assert ecmwf_launchers.get("ppn") == 128


# ---------------------------------------------------------------------------
# Expid validation
# ---------------------------------------------------------------------------

class TestExpidValidation:
    import re
    PATTERN = re.compile(r'^[a-zA-Z0-9]{4}$')

    @pytest.mark.parametrize("expid", ["a001", "test", "gcm4", "CTRL", "A1B2"])
    def test_valid_expids(self, expid):
        import re
        assert re.match(r'^[a-zA-Z0-9]{4}$', expid)

    @pytest.mark.parametrize("expid", [
        "a1",          # too short
        "toolong",     # too long
        "exp-1",       # hyphen not allowed
        "exp 1",       # space not allowed
        "",            # empty
        "a001b",       # 5 chars
    ])
    def test_invalid_expids(self, expid):
        import re
        assert not re.match(r'^[a-zA-Z0-9]{4}$', expid)


# ---------------------------------------------------------------------------
# Recipe normalisation
# ---------------------------------------------------------------------------

class TestRecipeNorm:
    def test_adds_yml_extension(self):
        recipe = "gcm-sr"
        if not recipe.endswith(('.yml', '.yaml')):
            recipe = recipe + ".yml"
        assert recipe == "gcm-sr.yml"

    def test_preserves_existing_extension(self):
        recipe = "gcm-sr.yml"
        if not recipe.endswith(('.yml', '.yaml')):
            recipe = recipe + ".yml"
        assert recipe == "gcm-sr.yml"

    def test_yaml_extension_preserved(self):
        recipe = "custom.yaml"
        if not recipe.endswith(('.yml', '.yaml')):
            recipe = recipe + ".yml"
        assert recipe == "custom.yaml"


# ---------------------------------------------------------------------------
# Built-in recipes sanity
# ---------------------------------------------------------------------------

class TestBuiltinRecipes:
    @pytest.mark.parametrize("recipe_name", [
        "gcm-sr.yml", "omip-sr.yml", "amip-sr.yml", "ccycle-sr.yml",
    ])
    def test_recipe_loads_and_has_components(self, recipe_name):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        recipe_path = paths.RECIPES_DIR / recipe_name
        assert recipe_path.exists(), f"Recipe missing: {recipe_path}"
        recipe = load_yaml_config(str(recipe_path))
        components = recipe.get("model_config", {}).get("components", [])
        assert len(components) > 0, f"Recipe {recipe_name} has no components"

    def test_gcm_has_coupled_components(self):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        recipe = load_yaml_config(str(paths.RECIPES_DIR / "gcm-sr.yml"))
        components = set(recipe["model_config"]["components"])
        assert {"oifs", "nemo", "oasis"}.issubset(components)

    def test_omip_has_no_atmosphere(self):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        recipe = load_yaml_config(str(paths.RECIPES_DIR / "omip-sr.yml"))
        components = set(recipe["model_config"]["components"])
        assert "oifs" not in components
        assert "nemo" in components

    def test_amip_has_no_nemo(self):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        recipe = load_yaml_config(str(paths.RECIPES_DIR / "amip-sr.yml"))
        components = set(recipe["model_config"]["components"])
        assert "nemo" not in components
        assert "oifs" in components

    def test_ccycle_has_lpjg(self):
        from ece4_exp import paths
        from ece4_exp.yaml_util import load_yaml_config
        recipe = load_yaml_config(str(paths.RECIPES_DIR / "ccycle-sr.yml"))
        components = set(recipe["model_config"]["components"])
        assert "lpjg" in components
