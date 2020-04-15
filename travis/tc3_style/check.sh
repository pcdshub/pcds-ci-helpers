#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

exit_code=0

_header "Checking that source code files do not contain tabs..."

tab_lines=$(./files.sh | xargs egrep $'\t')
tab_count=$(echo "${tab_lines}" | wc -l)
if [ "${tab_count}" -ne 0 ]; then
  echo "Found ${tab_count} lines with tabs"
  echo "${tab_lines}"
  exit_code=1
fi

_header "Checking for lines with trailing whitespace..."

bad_whitespace_lines=$(./files.sh | xargs egrep $' +$| +\r$')
bad_whitespace_count=$(echo "${bad_whitespace_lines}" | wc -l)
if [ "${bad_whitespace_count}" -ne 0 ]; then
  echo "Found ${bad_whitespace_count} lines with trailing whitespace"
  echo "${bad_whitespace_lines}"
  exit_code=2
fi

_header "Checking for TwinCAT misconfiguration (Line IDs)..."

lineid_lines=$(./files.sh | xargs grep 'LineId')
lineid_count=$(echo "${lineid_lines}" | wc -l)
if [ "${lineid_count}" -ne 0 ]; then
  echo "Found ${lineid_count} lines with same-file debug line ids (fix your twincat config)"
  echo "${lineid_lines}"
  exit_code=3
fi

_header "Style check exiting with code ${exit_code}"

exit $exit_code
