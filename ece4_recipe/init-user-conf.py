#!/usr/bin/env python3
import os
import re
import getpass
import shutil
from pathlib import Path

# Try to use yaml_util from the project
try:
    from .yaml_util import get_yaml, log_info, log_warn, COLOR_CYAN, COLOR_NC
    yaml_rt = get_yaml()
except ImportError:
    COLOR_CYAN = '\033[0;36m'
    COLOR_NC = '\033[0m'
    def log_info(msg): print(f"==> {msg}")
    def log_warn(msg): print(f"WARN: {msg}")
    yaml_rt = None

def scan_ssh_config(pattern):
    """Scan ~/.ssh/config for a User matching the regex pattern."""
    ssh_config = Path("~/.ssh/config").expanduser()
    if not ssh_config.exists():
        return None
    try:
        content = ssh_config.read_text()
        matches = re.findall(r'^\s*User\s+(' + pattern + r')\s*$', content, re.MULTILINE | re.IGNORECASE)
        if matches:
            return matches[0]
    except Exception:
        pass
    return None

def setup_user_conf():
    hub_user = getpass.getuser()
    # Simple rules: bsc032XXX for BSC, c3XXX for ECMWF
    bsc_user = scan_ssh_config(r'bsc032\d{3}')
    ecmwf_user = scan_ssh_config(r'c3\w+')
    
    as4_dir = Path("~/as4").expanduser()
    as4_dir.mkdir(parents=True, exist_ok=True)
    
    root_dir = Path(__file__).resolve().parent.parent
    src_dir = root_dir / "templates"

    # 1. Setup bsc32_platforms.yml
    plat_src = src_dir / "bsc32_platforms.yml"
    plat_dst = as4_dir / "bsc32_platforms.yml"
    if plat_src.exists() and not plat_dst.exists():
        log_info(f"Creating {COLOR_CYAN}{plat_dst}{COLOR_NC}")
        if yaml_rt:
            data = yaml_rt.load(plat_src)
            if "PLATFORMS" in data:
                for p_name, p_data in data["PLATFORMS"].items():
                    if p_name == "TRANSFER_NODE_BSCEARTH000":
                        p_data["USER"] = hub_user
                    elif bsc_user:
                        p_data["USER"] = bsc_user
            with open(plat_dst, 'w') as f:
                yaml_rt.dump(data, f)
        else:
            shutil.copy(plat_src, plat_dst)
    elif plat_dst.exists():
        log_warn(f"{plat_dst} already exists. Skipping.")

    # 2. Setup hpc2020_platforms.yml
    hpc_src = src_dir / "hpc2020_platforms.yml"
    hpc_dst = as4_dir / "hpc2020_platforms.yml"
    if hpc_src.exists() and not hpc_dst.exists():
        log_info(f"Creating {COLOR_CYAN}{hpc_dst}{COLOR_NC}")
        if yaml_rt:
            data = yaml_rt.load(hpc_src)
            if "PLATFORMS" in data and "ECMWF-HPC2020" in data["PLATFORMS"] and ecmwf_user:
                p = data["PLATFORMS"]["ECMWF-HPC2020"]
                p["USER"] = ecmwf_user
                if "SCRATCH_DIR" in p:
                    p["SCRATCH_DIR"] = re.sub(r'/c3[a-zA-Z0-9]+', f'/{ecmwf_user}', p["SCRATCH_DIR"])
            with open(hpc_dst, 'w') as f:
                yaml_rt.dump(data, f)
        else:
            shutil.copy(hpc_src, hpc_dst)
    elif hpc_dst.exists():
        log_warn(f"{hpc_dst} already exists. Skipping.")

    # 3. Setup ecearth4_user_config.yml and predefined_config.yml link
    conf_src = src_dir / "ecearth4_user_config.yml"
    conf_dst = as4_dir / "ecearth4_user_config.yml"
    link_dst = as4_dir / "predefined_config.yml"
    
    if conf_src.exists() and not conf_dst.exists():
        log_info(f"Creating {COLOR_CYAN}{conf_dst}{COLOR_NC}")
        shutil.copy(conf_src, conf_dst)
        if not link_dst.exists():
            log_info(f"Linking {COLOR_CYAN}{link_dst}{COLOR_NC} -> {conf_dst.name}")
            os.symlink(conf_dst.name, link_dst)
    elif conf_dst.exists():
        log_warn(f"{conf_dst} already exists. Skipping.")

    # 4. Setup ece4-recipe-completion.sh
    comp_src = src_dir / "ece4-recipe-completion.sh"
    comp_dst = as4_dir / "ece4-recipe-completion.sh"
    if comp_src.exists():
        log_info(f"Copying {COLOR_CYAN}{comp_dst}{COLOR_NC}")
        shutil.copy(comp_src, comp_dst)

    print(f"\n{COLOR_CYAN}Detected settings:{COLOR_NC}")
    print(f"  Hub User   : {hub_user}")
    print(f"  BSC User   : {bsc_user or 'NOT FOUND'}")
    print(f"  ECMWF User : {ecmwf_user or 'NOT FOUND'}")
    print(f"\n{COLOR_CYAN}Setup complete.{COLOR_NC}")
    print(f"1. Review configuration files in {COLOR_CYAN}~/as4{COLOR_NC}")
    print(f"2. Add your API tokens to {COLOR_CYAN}{conf_dst}{COLOR_NC}")
    print(f"3. To enable bash completion, add this to your {COLOR_CYAN}~/.bashrc{COLOR_NC}:")
    print(f"   {COLOR_CYAN}source {comp_dst}{COLOR_NC}")

if __name__ == "__main__":
    setup_user_conf()
