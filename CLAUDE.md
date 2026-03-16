# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a **documentation-only repository** for the LARA (Lab Automation Research Architecture) tutorial, built with MkDocs Material. It documents the PythonLab component — a Python-based language for defining laboratory automation workflows. There is no application source code to run or test.

## Commands

**Package manager:** `uv` (not pip directly)

```bash
# Serve docs locally with live reload
make serve
# or equivalently:
mkdocs serve --livereload

# Regenerate API reference docs from the pythonlab package
python generate_docs.py

# Install dependencies
uv sync

# Deploy to GitHub Pages (CI does this automatically on push to main)
mkdocs gh-deploy --force
```

## Architecture

### Documentation Structure (`docs/`)

- `index.md` — Landing page with LARA system architecture overview
- `quickstart.md` — Docker + Python setup guide for users
- `customization.md` — Guide for adapting LARA to a custom lab
- `pythonlab/` — PythonLab framework deep-dives (introduction, processes, API reference)
- `wrappers.md` — Device wrapper interface (SiLA2 standard)
- `assets/` — SVG logos and PNG screenshots

### Auto-generated API Docs

`generate_docs.py` introspects the installed `pythonlab` package (installed from the OSLA GitLab PyPI source) and uses `templates/api_reference.md.jinja2` to generate `docs/pythonlab/api_reference.md`. Run this script when the `pythonlab` package is updated to refresh the API reference.

### Key Concepts in the Docs

- **PythonLab language**: Python functions decorated as processes, converted to DAGs for scheduling
- **Resources**: Services (devices), Labware, Substances, Data — the four resource types
- **SiLA2**: The underlying device communication protocol
- **Orchestrator**: Schedules and executes process DAGs across lab devices

### MkDocs Configuration (`mkdocs.yml`)

Uses Material theme with: mermaid diagrams (mkdocs-mermaid2-plugin), image lightbox (mkdocs-glightbox), pan/zoom (mkdocs-panzoom-plugin), and mkdocstrings for API reference rendering.

### CI/CD

GitHub Actions (`.github/workflows/main.yml`) deploys to GitHub Pages on every push to `main` via `mkdocs gh-deploy --force`.

### Software packages
This documentation describes the usage of the LARA lab automation toolkit, which consists of the following software packages:

| Package | PyPI | GitLab Repository |
|---------|------|-------------------|
| PythonLab | [uuPythonlab](https://pypi.org/project/uuPythonlab/) | [pythonLab](https://gitlab.com/OpenLabAutomation/lab-automation-packages/pythonLab) |
| Lab Orchestrator | [uulaborchestrator](https://pypi.org/project/uulaborchestrator/) | [laborchestrator](https://gitlab.com/OpenLabAutomation/lab-automation-packages/laborchestrator) |
| Lab Scheduler | [uulabscheduler](https://pypi.org/project/uulabscheduler/) | [lab-scheduler](https://gitlab.com/OpenLabAutomation/lab-automation-packages/lab-scheduler) |
