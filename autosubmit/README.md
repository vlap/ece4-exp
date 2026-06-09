# Autosubmit Configuration Templates

These are template/example configuration files for using ece4-exp with **Autosubmit**.

## Files

- **asconf_vars.yml** - Variable mappings between Autosubmit and ece4-exp
- **compilation.yml** - Build configuration for Autosubmit
- **ecearth4_user_config.yml** - User configuration template
- **bsc32_platforms.yml** - BSC platform configuration example
- **hpc2020_platforms.yml** - ECMWF HPC2020 platform configuration example

## Usage

These files use Autosubmit's `%VARIABLE%` syntax for templating. If you're using ece4-exp in **standalone mode** (without Autosubmit), you don't need these files - use `~/.config/ece4-exp/defaults.yml` instead.

## Autosubmit Mode

For backward compatibility with Autosubmit workflows:

```bash
./ece4-exp generate --expdef expdef_EXPID.yml --jobs jobs_EXPID.yml
```

See the main README.md for more information.
