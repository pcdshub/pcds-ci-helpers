#!/bin/bash

pushd pcds-ci-helpers

export CI_HELPER_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" 

pushd travis

source settings.sh

if [[ ! -z "$LINT_PYTHON" ]]; then
    source python_linter.sh
fi

if [[ ! -z "$TWINCAT_SUMMARY" ]]; then
    source tc3_summary.sh
fi

if [[ ! -z "$TWINCAT_PRAGMALINT" ]]; then
    source tc3_pragmalint.sh
fi

if [[ ! -z "$TWINCAT_BUILD_DOCS" ]]; then
    bash tc3_linter.sh
    exit
fi

popd
popd
