#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

_header "Note: this is an experimental step and may report" \
        "errors where there are none. This will _not_ fail the" \
        "build."

pip install blark

find $TWINCAT_PROJECT_ROOT -name '*.sln' -exec blark parse -vv {} \;

_header "End of experimental parsing"
