#!/usr/bin/env bash
set -ex

# Ensure there are no errors.
python -W ignore manage.py check
python -W ignore manage.py makemigrations --dry-run --check

# Check flake
flake8 .

# Check imports
isort . --check-only --rr

# Run tests
python manage.py test --noinput --keepdb
