#!/bin/bash
# usage:
#   * set LINT_PYTHON to be the arguments to flake8 (e.g., package name)
#   * source `python_linter.sh` on Travis CI

if [ $TRAVIS ]; then
    cat <<EOF 1>&2
    WARNING: This script has been deprecated.
    Please use the new shared configuration yamls instead.
    Instructions for use can be found in the README.md at:
    https://github.com/pcdshub/pcds-ci-helpers
EOF
fi

pip install flake8

LINT_PYTHON_PATH=${LINT_PYTHON_PATH:-$TRAVIS_BUILD_DIR}

cd $LINT_PYTHON_PATH

linter_header=$(cat <<EOF
LINT_PYTHON_PATH: $PWD

=====================
Python linter results
=====================

EOF
)

linter_footer=$(cat <<'EOF'
=====================
EOF
)

echo "$linter_header"
echo "$ flake8 $LINT_PYTHON"
flake8 $LINT_PYTHON; FLAKE8_EXIT_CODE=$?
echo "$linter_footer"
if [ $FLAKE8_EXIT_CODE -ne 0 ]; then
    echo "Exit code: $FLAKE8_EXIT_CODE"
fi

sleep 1.0

exit $FLAKE8_EXIT_CODE
