#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

all_files=$(find $TWINCAT_PROJECT_ROOT -regextype posix-extended -regex '.*\.(TcPOU|TcDUT|TcGVL)$')
if [ -z "${TWINCAT_STYLE_EXCLUDE}" ]; then
  echo "${all_files}"
else
  echo "${all_files}" | egrep -v "${TWINCAT_STYLE_EXCLUDE}"
fi
