# AI Empire Repository Library

This directory contains cloned third-party repositories for research, evaluation, and integration into the AI Empire / Hermes-Archi system.

## How to Use

Each repository lives in its own subdirectory. See `MANIFEST.md` for the full catalog with purpose and status.

```bash
cd 09_LIBRARY/
ls -la
```

## Update All

```bash
bash 09_LIBRARY/update-all.sh
```

## Note

These repositories are excluded from the parent git repo via `.gitignore` because they are large and have their own history. Only `MANIFEST.md`, `README.md`, and `update-all.sh` are tracked.
