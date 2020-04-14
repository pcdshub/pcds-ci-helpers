#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

exit_code=0

_header "Checking that source code files do not contain tabs..."

tab_lines=$(./files.sh | xargs awk '/\t/' | wc -l)
if [ "${tab_lines}" -ne 0 ]; then
  echo "Found ${tab_lines} lines with tabs"
  exit_code=1
fi

_header "Checking for lines with trailing whitespace..."

bad_whitespace_lines=$(./files.sh | xargs egrep $' +$| +\r$' | wc -l)
if [ "${bad_whitespace_lines}" -ne 0 ]; then
  echo "Found ${bad_whitespace_lines} lines with trailing whitespace"
  exit_code=2
fi

_header "Checking for TwinCAT misconfiguration (Line IDs)..."

lineid_lines=$(./files.sh | xargs grep 'LineId' | wc -l)
if [ "${lineid_lines}" -ne 0 ]; then
  echo "Found ${lineid_lines} lines with same-file debug line ids (fix your twincat config)"
  exit_code=3
fi

_header "Style check exiting with code ${exit_code}"

exit $exit_code
