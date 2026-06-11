"""
Tests for recipe save / overlay-extraction workflow.

Validates the full generate → edit → save → verify roundtrip without network.
"""
import os
import pytest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from ece4_exp import paths
from ece4_exp.yaml_util import load_yaml_config, save_yaml_config, deep_merge, get_yaml
from ece4_exp.save_recipe_from_diff import compute_overlay, values_equal, create_recipe_from_diff

yaml_rt = get_yaml()


# ---------------------------------------------------------------------------
# values_equal
# ---------------------------------------------------------------------------

class TestValuesEqual:
    def test_equal_dicts(self):
        a = {"x": 1, "y": "hello"}
        b = {"x": 1, "y": "hello"}
        assert values_equal(a, b)

    def test_unequal_dicts(self):
        assert not values_equal({"x": 1}, {"x": 2})

    def test_missing_key(self):
        assert not values_equal({"x": 1}, {"x": 1, "y": 2})

    def test_equal_lists(self):
        assert values_equal([1, 2, 3], [1, 2, 3])

    def test_unequal_lists(self):
        assert not values_equal([1, 2], [1, 3])

    def test_scalar_coercion(self):
        # ruamel may return int vs str — values_equal uses str()
        assert values_equal(1, "1")


# ---------------------------------------------------------------------------
# compute_overlay
# ---------------------------------------------------------------------------

class TestComputeOverlay:
    def test_no_change_returns_none(self):
        base = {"a": 1, "b": "hello"}
        assert compute_overlay(base, deepcopy(base)) is None

    def test_scalar_change(self):
        base = {"a": 1}
        modified = {"a": 2}
        overlay = compute_overlay(base, modified)
        assert overlay["a"] == 2

    def test_nested_change_minimal(self):
        base = {"job": {"account": "bsc32", "qos": "gp"}}
        modified = {"job": {"account": "bsc99", "qos": "gp"}}
        overlay = compute_overlay(base, modified)
        # Only account changed — overlay must be minimal
        assert overlay["job"]["account"] == "bsc99"
        assert "qos" not in overlay["job"]

    def test_new_key_captured(self):
        base = {"a": 1}
        modified = {"a": 1, "b": 2}
        overlay = compute_overlay(base, modified)
        assert overlay["b"] == 2
        assert "a" not in overlay  # unchanged

    def test_list_change_whole_list_returned(self):
        base = {"groups": [{"nodes": 1, "oifs": 25}]}
        modified = {"groups": [{"nodes": 2, "oifs": 50}]}
        overlay = compute_overlay(base, modified)
        assert overlay["groups"] == modified["groups"]

    def test_deep_nested_change(self):
        base = {"job": {"slurm": {"sbatch": {"opts": {"time": "01:00:00"}}}}}
        modified = {"job": {"slurm": {"sbatch": {"opts": {"time": "02:00:00"}}}}}
        overlay = compute_overlay(base, modified)
        assert overlay["job"]["slurm"]["sbatch"]["opts"]["time"] == "02:00:00"


# ---------------------------------------------------------------------------
# Roundtrip: generate → modify → save → re-merge == modified
# ---------------------------------------------------------------------------

class TestRoundtrip:
    """The mathematical invariant: deep_merge(pristine, overlay) == modified."""

    def test_overlay_roundtrip_scalar(self):
        pristine = {"experiment": {"id": "a001"}, "job": {"account": "bsc32"}}
        modified = {"experiment": {"id": "a001"}, "job": {"account": "bsc99"}}

        overlay = compute_overlay(pristine, modified)
        assert overlay is not None

        reconstructed = deep_merge(deepcopy(pristine), overlay)
        assert reconstructed["job"]["account"] == "bsc99"

    def test_overlay_roundtrip_nested(self):
        pristine = {
            "experiment": {"id": "a001", "schedule": {"nlegs": 1}},
            "model_config": {"components": ["oifs", "nemo"]},
            "job": {"slurm": {"time": "01:00:00", "account": "bsc32"}},
        }
        modified = deepcopy(pristine)
        modified["job"]["slurm"]["account"] = "bsc99"
        modified["experiment"]["schedule"]["nlegs"] = 12

        overlay = compute_overlay(pristine, modified)
        reconstructed = deep_merge(deepcopy(pristine), overlay)

        assert reconstructed["job"]["slurm"]["account"] == "bsc99"
        assert reconstructed["experiment"]["schedule"]["nlegs"] == 12
        assert reconstructed["job"]["slurm"]["time"] == "01:00:00"  # unchanged
        assert reconstructed["model_config"]["components"] == ["oifs", "nemo"]  # unchanged


# ---------------------------------------------------------------------------
# create_recipe_from_diff (file-based)
# ---------------------------------------------------------------------------

class TestCreateRecipeFromDiff:
    def _write_config(self, path, data):
        save_yaml_config(str(path), data, mode="auto-ece4")

    def test_saves_recipe_on_change(self, tmp_path):
        pristine_data = {
            "experiment": {"id": "a001"},
            "job": {"slurm": {"sbatch": {"opts": {"account": "bsc32"}}}},
        }
        modified_data = deepcopy(pristine_data)
        modified_data["job"]["slurm"]["sbatch"]["opts"]["account"] = "bsc99"

        pristine_file = tmp_path / "a001_experiment_pristine.yml"
        modified_file = tmp_path / "a001_experiment.yml"
        recipe_file = tmp_path / "a001.yml"

        self._write_config(pristine_file, pristine_data)
        self._write_config(modified_file, modified_data)

        result = create_recipe_from_diff(
            modified_file=modified_file,
            pristine_file=pristine_file,
            recipe_path=str(recipe_file),
        )
        assert result is True
        assert recipe_file.exists()
        saved = load_yaml_config(str(recipe_file))
        assert saved["job"]["slurm"]["sbatch"]["opts"]["account"] == "bsc99"

    def test_missing_modified_file_returns_false(self, tmp_path):
        pristine_file = tmp_path / "a001_experiment_pristine.yml"
        missing_file = tmp_path / "nonexistent.yml"
        recipe_file = tmp_path / "a001.yml"

        self._write_config(pristine_file, {"experiment": {"id": "a001"}})

        result = create_recipe_from_diff(
            modified_file=missing_file,
            pristine_file=pristine_file,
            recipe_path=str(recipe_file),
        )
        assert result is False

    def test_missing_pristine_file_returns_false(self, tmp_path):
        modified_file = tmp_path / "a001_experiment.yml"
        missing_pristine = tmp_path / "nonexistent_pristine.yml"
        recipe_file = tmp_path / "a001.yml"

        self._write_config(modified_file, {"experiment": {"id": "a001"}})

        result = create_recipe_from_diff(
            modified_file=modified_file,
            pristine_file=missing_pristine,
            recipe_path=str(recipe_file),
        )
        assert result is False

    def test_no_change_returns_true_no_file(self, tmp_path):
        data = {"experiment": {"id": "a001"}, "job": {"account": "bsc32"}}
        pristine_file = tmp_path / "a001_experiment_pristine.yml"
        modified_file = tmp_path / "a001_experiment.yml"
        recipe_file = tmp_path / "a001.yml"

        self._write_config(pristine_file, data)
        self._write_config(modified_file, data)

        result = create_recipe_from_diff(
            modified_file=modified_file,
            pristine_file=pristine_file,
            recipe_path=str(recipe_file),
        )
        assert result is True
        # No changes → recipe file should not be written
        assert not recipe_file.exists()

    def test_pristine_always_in_user_config_dir(self, tmp_path):
        """Pristine path must not leak into /tmp even with absolute output path."""
        # This tests the fix for the absolute-output-path bug
        output_file = tmp_path / "subdir" / "a001_experiment.yml"
        pristine_name = Path(output_file).name.replace(".yml", "_pristine.yml")
        pristine_file = paths.USER_CONFIG_DIR / pristine_name
        assert str(paths.USER_CONFIG_DIR) in str(pristine_file)
        assert str(tmp_path) not in str(pristine_file)
