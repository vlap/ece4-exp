#!/usr/bin/env python3
"""
validate-experiment-config.py

Validates an experiment configuration by:
  1. Checking for well-formed YAML.
  2. Checking for well-formed Jinja2-like expressions in strings.
  3. Validating against a JSON schema.
"""

import argparse
import os
import sys
import re
import jsonschema
from .yaml_util import (
    load_yaml, log_info, log_error, log_warn, COLOR_CYAN, COLOR_NC
)

def to_plain_obj(obj):
    """
    Recursively convert ruamel.yaml objects (CommentedMap, TaggedScalar, etc.)
    to plain Python dicts, lists, and scalars for jsonschema.
    """
    if hasattr(obj, "items"):
        return {str(k): to_plain_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_plain_obj(x) for x in obj]
    elif hasattr(obj, "value") and hasattr(obj, "tag"):  # TaggedScalar
        return str(obj.value)
    else:
        return obj

# Basic schema for EC-Earth4 experiment configuration
SCHEMA = {
    "type": "object",
    "properties": {
        "experiment": {
            "type": "object",
            "required": ["id", "schedule"],
            "properties": {
                "id": {"type": "string"},
                "description": {"type": "string"},
                "schedule": {
                    "type": "object",
                    "required": ["all", "nlegs"],
                    "properties": {
                        "all": {"type": "string"},
                        "nlegs": {"type": "integer", "minimum": 1}
                    }
                },
            }
        },
        "job": {
            "type": "object",
            "required": ["launch"],
            "properties": {
                "launch": {
                    "type": "object",
                    "required": ["method"],
                    "properties": {
                        "method": {"type": "string"}
                    }
                }
            }
        },
        "model_config": {
            "type": "object",
            "required": ["components"],
            "properties": {
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "oifs": {"type": "object"},
                "nemo": {"type": "object"},
                "xios": {"type": "object"}
            }
        },
    },
    "required": ["experiment", "job", "model_config"]
}

def check_jinja2_syntax(content):
    """
    Basic check for Jinja2-like expressions {{ ... }}.
    """
    errors = []
    open_count = content.count("{{")
    close_count = content.count("}}")
    
    if open_count != close_count:
        errors.append(f"Mismatched Jinja2 delimiters: {open_count} '{{{{' and {close_count} '}}}}'")
    
    if re.search(r"\{\{.*\{\{", content):
        errors.append("Nested Jinja2 expressions found (not supported in this context)")
        
    return errors

def validate_config(config_path):
    """Validate the experiment configuration file."""
    if not os.path.exists(config_path):
        log_error(f"Configuration file not found: {config_path}")
        return False

    log_info(f"Validating {COLOR_CYAN}{config_path}{COLOR_NC}...")

    # 1. Read raw content for Jinja2 check
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_error(f"Failed to read file: {e}")
        return False

    jinja_errors = check_jinja2_syntax(content)
    if jinja_errors:
        for err in jinja_errors:
            log_error(f"Jinja2 Error: {err}")
        return False

    # 2. Load YAML
    try:
        data = load_yaml(config_path)
    except Exception as e:
        log_error(f"YAML Syntax Error: {e}")
        return False

    # 3. Extract configuration data (handling both auto-ece4 and ece4 formats)
    if isinstance(data, dict) and "ece4" in data:
        config_data = data["ece4"]
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "base.context" in data[0]:
        config_data = data[0]["base.context"]
    else:
        log_error("Invalid top-level structure. Expected 'ece4:' or '- base.context:'")
        return False

    # 4. JSON Schema Validation
    try:
        plain_config = to_plain_obj(config_data)
        jsonschema.validate(instance=plain_config, schema=SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        log_error(f"Schema Validation Error: {e.message}")
        log_error(f"At path: {' -> '.join(map(str, e.path))}")
        return False
    except jsonschema.exceptions.SchemaError as e:
        log_error(f"Internal Schema Error: {e.message}")
        return False

    log_info("Configuration is valid according to the schema.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate EC-Earth4 experiment configuration.")
    parser.add_argument("config", help="Path to the experiment YAML file")
    args = parser.parse_args()

    if validate_config(args.config):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
