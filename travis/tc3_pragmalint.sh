#!/bin/bash

source settings.sh

cd $TWINCAT_PROJECT_ROOT

pip install git+https://github.com/slaclab/pytmc.git@v2.4.0

EXIT_CODE=0

find . -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        echo "Pragma lint results"
        echo "-------------------"
        pytmc pragmalint --verbose "$tsproj"
        if [ $? -ne 0 ]; then
            EXIT_CODE=1
        fi
        echo ""
    done

find . -name '*.tmc' -print0 |
    while IFS= read -r -d '' tmc; do
        db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>/dev/null) 2>&1)

        echo "$(basename $tmc)"
        echo "=================="
        echo ""

        if [ ! -z "$db_errors" ]; then
            echo "Errors"
            echo "------"
            echo "$db_errors"
            echo ""

            if [ $? -ne 0 ]; then
                EXIT_CODE=2
            fi
        fi

        echo "Records"
        echo "-------"
        (pytmc db --allow-errors "$tmc" 2> /dev/null) | grep "^record" | sed -e 's/^record(\(.*\),\(.*\)).*$/\2 (\1)/' | sort
        echo ""

        echo "EPICS database"
        echo "--------------"
        pytmc db --allow-errors "$tmc" 2> /dev/null
    done

exit $EXIT_CODE
