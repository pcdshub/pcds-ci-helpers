#!/bin/bash
# usage: 
#   * set LINT_PYTHON to be the arguments to flake8 (e.g., package name)
#   * source `python_linter.sh` on Travis CI

pip install flake8
echo ""
printf '=%.0s' {1..100}
echo "Python linter results:"
flake8 $LINT_PYTHON
exit  # exits with the status of flake8
