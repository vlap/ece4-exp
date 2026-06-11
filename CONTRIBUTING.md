# Contributing to ece4-exp

Thank you for considering contributing to ece4-exp! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/vlap/ece4-exp/issues)
2. If not, create a new issue using the bug report template
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, ece4-exp version)
   - Error messages and logs

### Suggesting Features

1. Check if the feature has already been suggested in [Issues](https://github.com/vlap/ece4-exp/issues)
2. If not, create a new issue using the feature request template
3. Describe:
   - The problem your feature would solve
   - Your proposed solution
   - Use cases and benefits
   - Alternative approaches you've considered

### Contributing Code

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp

# Install in editable mode
pip install -e .

# Test installation
ece4-exp --help
ece4-exp list
```

#### Development Workflow

1. **Fork the repository** on GitHub

2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/issue-123
   ```

3. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**:
   ```bash
   # Test CLI commands
   ece4-exp list
   ece4-exp generate --recipe gcm-sr.yml --sim-procs 1120 --expid test --dry-run
   ece4-exp validate test.yml
   
   # Test on different Python versions if possible
   python3.8 -m ece4_exp.cli --help
   python3.11 -m ece4_exp.cli --help
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of what you added"
   ```
   
   Commit message format:
   - `Add feature: ...` for new features
   - `Fix: ...` for bug fixes
   - `Update docs: ...` for documentation
   - `Refactor: ...` for code improvements

6. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create a Pull Request**:
   - Go to the main repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Link related issues

#### Code Style Guidelines

- **Python**: Follow PEP 8
- **Line length**: Max 100 characters (flexible)
- **Imports**: Group by standard library, third-party, local
- **Documentation**: Update README.md and docs/source/ for user-facing changes
- **Comments**: Explain "why", not "what"

#### Adding New Features

**New Recipes:**
```bash
# Add recipe to recipes/ directory
recipes/my-new-recipe.yml

# Test it
ece4-exp generate my-new-recipe 10 test --dry-run
```

**New Platforms:**
```bash
# Add platform to platforms/ directory
platforms/my-platform.yml

# Include:
# - ppn (processors per node)
# - launcher configurations
# - platform-specific settings
```

**New Commands:**
1. Add function to `ece4_exp/cli.py`
2. Add argparse subcommand
3. Test thoroughly
4. Update documentation

#### Testing Checklist

Before submitting PR:

- [ ] Code works on your machine
- [ ] No hardcoded paths or credentials
- [ ] Error messages are clear and helpful
- [ ] Documentation updated (README, docs/source/)
- [ ] Help text added/updated for new options
- [ ] Examples use 4-character expids
- [ ] No new dependencies without discussion

### Contributing Documentation

Documentation improvements are always welcome!

**Types of documentation:**
- README.md - Quick start guide
- docs/source/index.rst - Overview and quick start
- docs/source/reference.rst - Complete command reference
- Code comments - Inline explanations
- Help text - CLI --help output

**Documentation style:**
- Clear and concise
- Include examples
- Test all commands shown
- Keep consistent with existing docs

### Adding Recipes or Platforms

**New Recipe Contributions:**
1. Create recipe YAML in `recipes/`
2. Test thoroughly on your platform
3. Document what it configures
4. Provide example usage

**New Platform Contributions:**
1. Create platform YAML in `platforms/`
2. Include all required fields
3. Test on the actual platform
4. Document platform-specific requirements

## Review Process

1. **Automated checks** run on all PRs (when CI is set up)
2. **Maintainer review** - usually within 1 week
3. **Feedback** - address reviewer comments
4. **Merge** - once approved, changes are merged

## Release Process

Releases are managed by maintainers:

1. Version bump in `pyproject.toml`
2. Update `docs/CHANGES.md`
3. Create git tag
4. Build package: `python -m build`
5. Upload to PyPI: `twine upload dist/*`
6. Create GitHub release

## Questions?

- **General questions**: Open a [Discussion](https://github.com/vlap/ece4-exp/discussions)
- **Bug reports**: Open an [Issue](https://github.com/vlap/ece4-exp/issues)
- **Direct contact**: vladimir.lapin@bsc.es

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- ACKNOWLEDGMENTS file (if created)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ece4-exp!** 🎉
