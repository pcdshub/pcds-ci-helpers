#!/bin/bash

pushd pcds-ci-helpers/travis

if [[ ! -z "$LINT_PYTHON" ]]; then
    source python_linter.sh
fi

popd
