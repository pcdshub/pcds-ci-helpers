#!/bin/bash

pushd pcds-ci-helpers

export CI_HELPER_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "** pcds-ci-helpers version: $(git describe --tags --always) **"

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

if [[ ! -z "$TWINCAT_STYLE" ]]; then
    pushd tc3_style
    bash check.sh; exit_code=$?
    # Attempt parsing the code, but use the return code from the simple check
    # script
    bash parse.sh
    exit $exit_code
fi

if [[ ! -z "$PRE_COMMIT" ]]; then
    source pre_commit.sh
fi

popd
popd
