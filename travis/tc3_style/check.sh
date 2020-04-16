#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

exit_code=0

_header "Checking that source code files do not contain leading tabs..."

tab_lines=$(./files.sh | xargs grep -En $'^\s*\t')
if [ -n "${tab_lines}" ]; then
  tab_count=$(echo "${tab_lines}" | wc -l)
  echo "Found ${tab_count} lines with leading tabs"
  echo "${tab_lines}"
  exit_code=1
else
  echo "Found no lines with tabs!"
fi

_header "Checking for lines with trailing whitespace..."

whitespace_lines=$(./files.sh | xargs grep -En $' +$| +\r$')
if [ -n "${whitespace_lines}" ]; then
  whitespace_count=$(echo "${whitespace_lines}" | wc -l)
  echo "Found ${whitespace_count} lines with trailing whitespace"
  echo "${whitespace_lines}"
  exit_code=2
else
  echo "Found no lines with trailing whitespace!"
fi

_header "Checking for TwinCAT misconfiguration (Line IDs)..."

lineid_lines=$(./files.sh | xargs grep -n 'LineId')
if [ -n "${lineid_lines}" ]; then
  lineid_count=$(echo "${lineid_lines}" | wc -l)
  echo "Found ${lineid_count} lines with same-file debug line ids (fix your twincat config)"
  echo "${lineid_lines}"
  exit_code=3
else
  echo "Found no debug line ids!"
fi

_header "Style check exiting with code ${exit_code}"

exit $exit_code
