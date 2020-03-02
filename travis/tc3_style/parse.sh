#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

pip install blark

find $TWINCAT_PROJECT_ROOT -name '*.sln' -exec blark parse -vv {} \;
