#!/bin/bash

pushd pcds-ci-helpers

export CI_HELPER_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 

pushd travis

if [[ ! -z "$LINT_PYTHON" ]]; then
    source python_linter.sh
fi

if [[ ! -z "$TWINCAT_SUMMARY" ]]; then
    source tc3_summary.sh
fi

popd
popd
