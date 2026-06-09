# ece4-exp: Where Is Everything?

## 🎤 Presentation Materials

### Slides (Ready to Present!)
- **HTML (web):** `docs/presentation/ece4-exp-intro.html` (154 KB, 38 slides)
- **PDF (print):** `docs/presentation/ece4-exp-intro.pdf` (171 KB, 38 slides)
- **Markdown (source):** `docs/presentation/ece4-exp-intro.md` (13 KB, editable)

**Open in browser:**
```bash
firefox docs/presentation/ece4-exp-intro.html
# or
xdg-open docs/presentation/ece4-exp-intro.pdf
```

## 🎬 Demos

### Quick Interactive Demo (2 minutes)
```bash
./QUICK_DEMO.sh
```
Shows:
- List recipes
- Generate GCM config (10 nodes)
- Generate OMIP config (2 nodes)
- Validate configs
- What you get

### Full Demo Script (10 minutes)
**File:** `DEMO.md`

Complete walkthrough with:
- Problem statement
- Setup process
- Multiple experiment types
- Layering explanation
- Reproducibility
- Q&A sections

## 📚 Documentation

### User Documentation
- **README.md** - Complete user guide with examples
- **docs/CHANGES.md** - Migration guide and changelog

### Setup
- **setup.sh** - One-command installation
- **setup.sh --interactive** - Guided setup with prompts

## 🏗️ Repository Structure

```
ece4-exp/
├── 📊 PRESENTATION & DEMO
│   ├── docs/presentation/
│   │   ├── ece4-exp-intro.html  ← OPEN THIS IN BROWSER
│   │   ├── ece4-exp-intro.pdf   ← OR THIS
│   │   └── ece4-exp-intro.md    (source)
│   ├── DEMO.md                  ← Full demo script
│   ├── QUICK_DEMO.sh            ← Run this! Interactive
│   └── WHERE_IS_EVERYTHING.md   ← You are here
│
├── 🚀 USER TOOLS
│   ├── ece4-exp                 ← Main command
│   ├── setup.sh                 ← Setup script
│   └── scripts/
│       └── ece4-exp-completion.sh
│
├── 📖 DOCUMENTATION
│   ├── README.md                ← Start here
│   ├── docs/
│   │   ├── CHANGES.md
│   │   └── examples/
│
├── 📋 TEMPLATES
│   └── templates/
│       └── autosubmit/          ← Autosubmit config templates
│
├── 🧪 RECIPES
│   ├── recipes/
│   │   ├── gcm-sr.yml           ← Coupled GCM
│   │   ├── omip-sr.yml          ← Ocean-only
│   │   ├── amip-sr.yml          ← Atmosphere-only
│   │   ├── ccycle-sr.yml        ← Carbon cycle
│   │   └── weekly_tests/
│
├── 🔧 PLATFORM CONFIGS
│   └── platforms/
│       ├── bsc-marenostrum5/
│       └── ecmwf-hpc2020/
│
└── 💻 PYTHON PACKAGE
    └── ece4_exp/
        ├── generate-experiment-config.py
        ├── validate-experiment-config.py
        └── ...
```

## 🎯 Quick Start for Presenters

### Option 1: Live Demo During Talk
1. Open slides: `docs/presentation/ece4-exp-intro.html`
2. Have terminal ready with `./QUICK_DEMO.sh`
3. At slide 25-30 (demo section), switch to terminal
4. Run the quick demo (2 min)
5. Return to slides for summary

### Option 2: Self-Contained Presentation
1. Open slides: `docs/presentation/ece4-exp-intro.html`
2. Present all 38 slides (includes example outputs)
3. Q&A using DEMO.md as reference

### Option 3: Workshop Format
1. Distribute link to repo
2. Have attendees run `./setup.sh --interactive`
3. Walk through `DEMO.md` together
4. Let them try different recipes

## 📧 Sharing the Tool

### Email Template
```
Subject: Introducing ece4-exp: EC-Earth4 Configuration Made Simple

Hi team,

I'd like to share a tool that makes EC-Earth4 experiment configuration
much easier: ece4-exp

🎯 What it does:
- Generates EC-Earth4 configs in 30 seconds (vs 2-4 hours manual)
- Pre-tested recipes for GCM, OMIP, AMIP, etc.
- Fetches settings from upstream EC-Earth4 repo automatically
- Validates before you submit

📊 See the presentation:
https://your-domain/ece4-exp/docs/presentation/ece4-exp-intro.html

🚀 Try it:
git clone https://github.com/vlap/ece4-exp.git
cd ece4-exp
./setup.sh

Questions? Reply to this email or check the README.md

Cheers,
[Your name]
```

### Slack/Teams Message
```
🎉 New tool: ece4-exp makes EC-Earth4 configs easy!

✅ 30 seconds instead of 2-4 hours
✅ Pre-tested recipes (GCM, OMIP, AMIP, etc.)
✅ Auto-fetches platform settings

📊 Slides: https://link-to-slides
💻 Code: https://github.com/vlap/ece4-exp

Try: `git clone ... && ./setup.sh`
```

## 🎓 Training Materials

### For New Users
1. Show slides 1-15 (problem, solution, examples)
2. Run `./QUICK_DEMO.sh` together
3. Have them run `./setup.sh --interactive`
4. Help them generate first config
5. Point to README.md for details

### For Experienced Users
1. Show slides 16-25 (layering, flexibility)
2. Demonstrate recipe extraction
3. Show how to create custom recipes
4. Integration with existing workflows

## 🐛 Troubleshooting Demos

**If demo fails:**
- Check: `./ece4-exp list` works
- Check: `~/.config/ece4-exp/defaults.yml` exists
- Run: `./ece4-exp --help` to verify installation
- Fallback: Show slides only (outputs are included)

**Clean state for re-runs:**
```bash
rm -f demo-*.yml *_experiment.yml
rm -rf external/ece4_yml_repo
```

## 📞 Support

**For questions during presentation:**
- Check: DEMO.md (Q&A section at bottom)
- Check: README.md (detailed docs)
- GitHub issues: https://github.com/vlap/ece4-exp/issues

**Contact:**
Vladimir Lapin (BSC): vladimir.lapin@bsc.es

---

**TL;DR:**
- **Slides:** `docs/presentation/ece4-exp-intro.{html,pdf}`
- **Quick demo:** `./QUICK_DEMO.sh`
- **Full demo:** `DEMO.md`
- **Setup:** `./setup.sh`
