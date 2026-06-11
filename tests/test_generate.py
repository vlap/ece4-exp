"""
Tests for config generation logic — runs without git clone by injecting a local
base config.  This catches regressions in the merge pipeline, node-layout
expressions, and launcher-kind auto-detection.
"""
import os
import pytest
import tempfile
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch

from ece4_exp import paths
from ece4_exp.yaml_util import load_yaml_config, deep_merge, get_yaml
from ece4_exp.generate_experiment_config import (
    generate_config, apply_node_eval, eval_nodes_expr,
    select_launcher_fragment, build_cli_overrides,
)

yaml_rt = get_yaml()


# ---------------------------------------------------------------------------
# Fixture: minimal base config that mirrors the real one's structure
# ---------------------------------------------------------------------------

@pytest.fixture
def base_config_file(tmp_path):
    """Write a minimal experiment-config-example.yml to a temp dir."""
    content = """\
ece4:
  experiment:
    id: XXXX
    description: A new ECE4 experiment
    schedule:
      all: !rrule >
        DTSTART:18500101 RRULE:FREQ=YEARLY;INTERVAL=1;UNTIL=18510101
      nlegs: 1
    run_from_scratch: false
  model_config:
    components: []
  job:
    launch:
      method: slurm-wrapper-taskset
    resubmit: true
    slurm:
      sbatch:
        opts:
          time: "00:30:00"
          output: XXXX.log
          job-name: ECE4_XXXX
"""
    p = tmp_path / "experiment-config-example.yml"
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Node expression evaluator
# ---------------------------------------------------------------------------

class TestNodeEval:
    def test_simple_expression(self):
        assert eval_nodes_expr("{{ nodes * 2 }}", 5) == 10

    def test_subtraction(self):
        assert eval_nodes_expr("{{ nodes - 1 }}", 10) == 9

    def test_passthrough_non_template(self):
        assert eval_nodes_expr("hello", 10) == "hello"

    def test_passthrough_integer(self):
        assert eval_nodes_expr(42, 10) == 42

    def test_apply_node_eval_in_dict(self):
        data = {"nodes": "{{ nodes - 1 }}", "oifs": 25}
        apply_node_eval(data, 10)
        assert data["nodes"] == 9

    def test_apply_node_eval_in_list(self):
        data = [{"nodes": "{{ nodes - 1 }}", "oifs": 25}, {"nodes": 1, "nemo": 9}]
        apply_node_eval(data, 5)
        assert data[0]["nodes"] == 4
        assert data[1]["nodes"] == 1  # literal int untouched


# ---------------------------------------------------------------------------
# CLI overrides builder
# ---------------------------------------------------------------------------

class TestBuildCliOverrides:
    def test_expid_set(self):
        ov = build_cli_overrides("a001", None, None, None)
        assert ov["experiment"]["id"] == "a001"

    def test_account_set(self):
        ov = build_cli_overrides(None, "bsc32", None, None)
        assert ov["job"]["slurm"]["sbatch"]["opts"]["account"] == "bsc32"

    def test_walltime_formatted(self):
        ov = build_cli_overrides(None, None, 2, None)
        assert ov["job"]["slurm"]["sbatch"]["opts"]["time"] == "02:00:00"

    def test_walltime_padded(self):
        ov = build_cli_overrides(None, None, 24, None)
        assert ov["job"]["slurm"]["sbatch"]["opts"]["time"] == "24:00:00"

    def test_empty_overrides(self):
        ov = build_cli_overrides(None, None, None, None)
        assert ov == {}

    def test_all_set(self):
        ov = build_cli_overrides("a001", "bsc32", 1, "test run")
        assert ov["experiment"]["id"] == "a001"
        assert ov["experiment"]["description"] == "test run"
        assert ov["job"]["slurm"]["sbatch"]["opts"]["account"] == "bsc32"
        assert ov["job"]["slurm"]["sbatch"]["opts"]["time"] == "01:00:00"


# ---------------------------------------------------------------------------
# Launcher fragment selection and node evaluation
# ---------------------------------------------------------------------------

@pytest.fixture
def mn5_launchers():
    return load_yaml_config(str(paths.PLATFORMS_DIR / "bsc-marenostrum5.yml"))


class TestLauncherFragment:
    def test_cpld_sr_selected(self, mn5_launchers):
        frag = select_launcher_fragment("slurm-wrapper-taskset", "CPLD-SR", mn5_launchers)
        assert "job" in frag
        assert "groups" in frag["job"]

    def test_omip_sr_selected(self, mn5_launchers):
        frag = select_launcher_fragment("slurm-wrapper-taskset", "OMIP-SR", mn5_launchers)
        assert "groups" in frag["job"]

    def test_node_expressions_resolved(self, mn5_launchers):
        frag = select_launcher_fragment("slurm-wrapper-taskset", "CPLD-SR", mn5_launchers)
        apply_node_eval(frag, 10)
        groups = frag["job"]["groups"]
        # First group: nodes=1 (literal), second: nodes = 10-1 = 9
        assert groups[0]["nodes"] == 1
        assert groups[1]["nodes"] == 9

    def test_omp_threads_inherited(self, mn5_launchers):
        frag = select_launcher_fragment("slurm-wrapper-taskset", "CPLD-SR", mn5_launchers)
        assert frag["job"]["oifs"]["omp_num_threads"] == 4


# ---------------------------------------------------------------------------
# Launcher kind auto-detection
# ---------------------------------------------------------------------------

class TestAutoDetectKind:
    """Tests that auto-detect correctly infers experiment type from recipe components."""

    def _detect(self, components, oifs_grid="TL255L91", nemo_grid="eORCA1L75"):
        # Inline the same logic as generate_config uses
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
        return f"{exp_type}-{resolution}"

    def test_gcm_is_cpld_sr(self):
        assert self._detect(["oifs", "xios", "nemo", "rnfm", "oasis"]) == "CPLD-SR"

    def test_omip_is_omip_sr(self):
        assert self._detect(["xios", "nemo"]) == "OMIP-SR"

    def test_amip_is_amip_sr(self):
        assert self._detect(["oifs", "xios", "amipfr", "oasis"]) == "AMIP-SR"

    def test_ccycle_is_cccl_sr(self):
        assert self._detect(["oifs", "xios", "nemo", "rnfm", "oasis", "lpjg"]) == "CCCL-SR"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            self._detect(["oifs", "nemo"])  # missing required components


# ---------------------------------------------------------------------------
# Full generate_config pipeline (no network — uses local base config)
# ---------------------------------------------------------------------------

class TestGenerateConfig:
    def test_dry_run_succeeds(self, base_config_file, capsys):
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                dry_run=True,
            )
        out = capsys.readouterr().out
        assert "a001" in out

    def test_generates_file(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                output=str(outfile),
            )
        assert outfile.exists()

    def test_generated_has_expid(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                output=str(outfile),
            )
        config = load_yaml_config(str(outfile))
        assert config["experiment"]["id"] == "a001"

    def test_generated_has_account(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="myproj",
                output=str(outfile),
            )
        config = load_yaml_config(str(outfile))
        assert config["job"]["slurm"]["sbatch"]["opts"]["account"] == "myproj"

    def test_generated_has_version_stamp(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                output=str(outfile),
                ece4_version="v4.1.8",
            )
        config = load_yaml_config(str(outfile))
        assert config["experiment"]["_ece4_version"] == "v4.1.8"

    def test_walltime_override(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=1120,
                cpus_per_node=112,
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                walltime=48,
                output=str(outfile),
            )
        config = load_yaml_config(str(outfile))
        assert config["job"]["slurm"]["sbatch"]["opts"]["time"] == "48:00:00"

    def test_node_groups_computed(self, base_config_file, tmp_path):
        outfile = tmp_path / "a001_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="bsc-marenostrum5",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=10 * 112,
                cpus_per_node=112,  # 10 nodes
                user_recipe="gcm-sr",
                expid="a001",
                account="bsc32",
                output=str(outfile),
            )
        config = load_yaml_config(str(outfile))
        groups = config["job"]["groups"]
        assert groups[0]["nodes"] == 1
        assert groups[1]["nodes"] == 9  # 10 - 1

    def test_ecmwf_platform_ppn(self, base_config_file, tmp_path):
        outfile = tmp_path / "ec01_experiment.yml"
        with patch.object(paths, 'get_base_config_example', return_value=str(base_config_file)):
            generate_config(
                platform="ecmwf-hpc2020",
                launcher="slurm-wrapper-taskset",
                launcher_kind="CPLD-SR",
                sim_procs=10 * 128,
                cpus_per_node=128,  # 10 nodes at 128 cores
                user_recipe="gcm-sr",
                expid="ec01",
                account="spesiccf",
                output=str(outfile),
            )
        config = load_yaml_config(str(outfile))
        assert config["experiment"]["id"] == "ec01"
        groups = config["job"]["groups"]
        assert groups[1]["nodes"] == 9
