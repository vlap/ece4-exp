"""
Module to load and manipulate yaml file with ruamel package

Authors
Original: Matteo Nurisso (CNR-ISAC, Mar 2024)
Adapted:  Vladimir Lapin (BSC,      Mar 2026)
"""
import os
import sys
import re
from copy import deepcopy
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PlainScalarString
from ruamel.yaml.comments import TaggedScalar, CommentedSeq

# --- Colors & Logging ---
COLOR_NC = '\033[0m'
COLOR_GREEN = '\033[0;32m'
COLOR_CYAN = '\033[0;36m'
COLOR_YELLOW = '\033[1;33m'
COLOR_RED = '\033[0;31m'

def log_info(msg):
    print(f"{COLOR_GREEN}==>{COLOR_NC} {msg}")

def log_warn(msg):
    print(f"{COLOR_YELLOW}WARN:{COLOR_NC} {msg}")

def log_error(msg):
    print(f"{COLOR_RED}ERROR:{COLOR_NC} {msg}", file=sys.stderr)

def log_yaml(data):
    """
    Print YAML data with syntax highlighting if pygments is available and output is a TTY.
    """
    from io import StringIO
    yaml_rt = get_yaml()
    buf = StringIO()
    yaml_rt.dump(data, buf)
    text = buf.getvalue()

    if sys.stdout.isatty():
        try:
            from pygments import highlight
            from pygments.lexers import YamlLexer
            from pygments.formatters import TerminalFormatter
            print(highlight(text, YamlLexer(), TerminalFormatter()))
        except ImportError:
            print(text)
    else:
        print(text)

def get_yaml(typ='rt'):
    """
    Returns a pre-configured ruamel.yaml.YAML object.
    """
    yaml = YAML(typ=typ)
    yaml.preserve_quotes = True
    yaml.width = 4096
    if typ == 'rt':
        yaml.default_flow_style = None  # preserves inline where possible
    return yaml

def expand_env_vars(obj):
    """Recursively expand environment variables in a dictionary or list."""
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        return os.path.expandvars(obj)
    else:
        return obj

def load_yaml(file: str= None, ruamel_type: str = 'rt', expand_env: bool = False):
    """
    Load yaml file with ruamel.yaml package
    """
    if not os.path.exists(file):
        raise ValueError(f'File {file} not found: you need to have this configuration file!')

    yaml = get_yaml(typ=ruamel_type)
    
    with open(file, 'r', encoding='utf-8') as f:
        cfg = yaml.load(f)

    if expand_env:
        cfg = expand_env_vars(cfg)

    return cfg

def save_yaml(path: str = None, cfg: dict = None, ruamel_type: str = 'rt'):
    """
    Save dictionary to a yaml file with ruamel.yaml package
    """
    yaml = get_yaml(typ=ruamel_type)

    if path is None:
        raise ValueError('File not defined')
    if cfg is None:
        raise ValueError('Content cfg not defined')

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(cfg, f)

def load_yaml_config(path: str):
    """Load and validate a YAML config file, supporting both:
       - ece4 convention:       "- base.context:"
       - auto-ece4 convention:  "ece4:"
    """
    if not os.path.exists(path):
        log_error(f"Configuration file not found: {path}")
        sys.exit(1)

    data = load_yaml(path)

    # ece4 format
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "base.context" in data[0]:
            return data[0]["base.context"]
        raise ValueError(f"{path} must start with '- base.context:'")

    # auto-ece4 format
    if isinstance(data, dict):
        if "ece4" in data:
            return data["ece4"]
        raise ValueError(f"{path} must start with 'ece4:'")

    raise ValueError(f"{path} has unsupported YAML structure")

def load_platform_yaml(path: str):
    """Load ecearth4 platform file and extract all base.context sections.

    Platform files can have multiple tasks, but we only want the base.context parts.
    Returns a merged dict of all base.context sections found.
    """
    if not os.path.exists(path):
        return {}

    data = load_yaml(path)

    if not isinstance(data, list):
        return {}

    # Merge all base.context sections found in the file
    merged = {}
    for item in data:
        if isinstance(item, dict) and "base.context" in item:
            deep_merge(merged, item["base.context"])

    return merged


def save_yaml_config(path: str, cfg: dict, mode: str = "auto-ece4"):
    """Save config in old or new format."""
    if mode == "ece4":
        obj = [{"base.context": cfg}]
    elif mode == "auto-ece4":
        obj = {"ece4": cfg}
    else:
        raise ValueError("mode must be 'ece4' or 'auto-ece4'")

    save_yaml(path, obj)

def deep_merge(base, overlay):
    """Recursively merge overlay into base."""
    if base is None:
        return deepcopy(overlay)
    if overlay is None:
        return base
    if hasattr(base, "items") and hasattr(overlay, "items"):
        for k, v in overlay.items():
            if k in base and hasattr(base[k], "items") and hasattr(v, "items"):
                deep_merge(base[k], v)
            else:
                base[k] = deepcopy(v)
        return base
    if isinstance(base, list) and isinstance(overlay, list):
        return base + overlay
    return deepcopy(overlay)

def unquote_percent_variables(filepath: str) -> None:
    """
    Remove quotes only when the RHS is exactly "%VAR%" or '%VAR%'.
    """
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match: : "%VAR%"  OR  : '%VAR%'
    content = re.sub(r':\s*"(%[A-Za-z0-9_.]+%)"', r': \1', content)
    content = re.sub(r":\s*'(%[A-Za-z0-9_.]+%)'", r': \1', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def quote_percent_variables(filepath: str) -> None:
    """
    Add quotes to RHS when it is exactly %VAR% and unquoted.
    """
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match: : %VAR% (unquoted)
    # Ensure it's not already quoted and is followed by space or newline
    content = re.sub(r':\s+(%[A-Za-z0-9_.]+%)(\s|$)', r': "\1"\2', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def noparse_block(value):
    """
    Create a block scalar with the !noparse tag.
    """
    return TaggedScalar(value, tag="!noparse", style='"')

def list_block(value):
    """
    Create a PlanScalar with a list
    """
    return _list_compact([PlainScalarString(x) for x in value])

def _list_compact(list):
    """
    Create a compact list in CommentedSeq format.
    """
    comm = CommentedSeq(list)
    comm.fa.set_flow_style()
    return comm
