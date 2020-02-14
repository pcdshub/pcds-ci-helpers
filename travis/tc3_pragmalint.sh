#!/bin/bash

source settings.sh

cd $TWINCAT_PROJECT_ROOT

pip install pytmc

EXIT_CODE=0

while IFS= read -r -d '' tsproj; do 
    echo "Pragma lint results"
    echo "-------------------"
    pytmc pragmalint --verbose "$tsproj"
    if [ $? -ne 0 ]; then
        EXIT_CODE=1
    fi
    echo ""
done < <(find . -name '*.tsproj' -print0)

while IFS= read -r -d '' tmc; do
    db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>/dev/null) 2>&1)

    echo "$(basename $tmc)"
    echo "=================="
    echo ""

    if [ ! -z "$db_errors" ]; then
        EXIT_CODE=2
        echo "Errors"
        echo "------"
        echo "$db_errors"
        echo ""
    fi

    echo "Records"
    echo "-------"
    (pytmc db --allow-errors "$tmc" 2> /dev/null) | grep "^record" | sed -e 's/^record(\(.*\),\(.*\)).*$/\2 (\1)/' | sort
    echo ""

    echo "EPICS database"
    echo "--------------"
    pytmc db --allow-errors "$tmc" 2> /dev/null
done < <(find . -name '*.tmc' -print0)

if [ $EXIT_CODE -ne 0 ]; then
    echo "tc3_pragmalint.sh is exiting with code: $EXIT_CODE"
fi
exit $EXIT_CODE
