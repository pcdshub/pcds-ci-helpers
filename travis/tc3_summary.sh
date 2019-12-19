!/bin/bash

TWINCAT_PROJECT_ROOT=${TWINCAT_PROJECT_ROOT:-$TRAVIS_BUILD_DIR}

cd $TWINCAT_PROJECT_ROOT

pip install git+https://github.com/slaclab/pytmc.git@v2.4.0

# Execute linting script:
find . -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        pytmc summary --all --code --markdown "$tsproj"
        echo "Pragma lint results"
        echo "-------------------"
        echo '```'
        pytmc pragmalint --verbose "$tsproj"
        echo '```'
    done

find . -name '*.tmc' -print0 |
    while IFS= read -r -d '' tmc; do
        db_filename=$DOCS_SOURCE_PATH/$(basename $tmc).db
        db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>$db_filename) 2>&1)
        md_filename=$DOCS_SOURCE_PATH/$(basename $tmc).md

        echo "$(basename $tmc)"
        echo "=================="
        echo ""

        if [ ! -z "$db_errors" ]; then
            echo "Errors"
            echo "------"
            echo '```'
            echo "$db_errors"
            echo '```'
            echo ""
        fi

        echo "Records"
        echo "-------"
        echo '```'
        grep "^record" $db_filename | sed -e 's/^record(\(.*\),\(.*\)).*$/\2 (\1)/' | sort
        echo '```'
        echo ""

        echo "EPICS database"
        echo "--------------"
        echo '```'
        cat $db_filename
        echo '```'
    done

exit 0
