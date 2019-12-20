#!/bin/bash

# tc3linter.sh 

LINTER_PYTHON_VERSION=3.7

source settings.sh

pip install git+https://github.com/slaclab/pytmc.git@v2.4.0

# install docs
pip install sphinx recommonmark

# Allow user to configure path for documentation drop site 
DEFAULT_DOCS_PATH="$TRAVIS_BUILD_DIR/docs"
DEFAULT_DOCS_SOURCE_PATH="$TRAVIS_BUILD_DIR/docs/source"

echo "PYTMC version:"
echo $(pytmc --version)

if [ -z $1 ]; then
    DOCS_SOURCE_PATH=$DEFAULT_DOCS_SOURCE_PATH
    DOCS_PATH=$DEFAULT_DOCS_PATH
else
    DOCS_SOURCE_PATH=$1
    DOCS_PATH=$2
fi
   
if [ ! -d $DOCS_SOURCE_PATH ]; then
    mkdir -p $DOCS_SOURCE_PATH
    cp -r ${CI_HELPER_PATH}/travis/docs_template_files/* $DOCS_PATH/
fi

# Execute linting script:
find $TWINCAT_PROJECT_ROOT -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        pytmc summary --all --code --markdown "$tsproj" > $DOCS_SOURCE_PATH/$(basename $tsproj).md;
        echo "Pragma lint results" >> $DOCS_SOURCE_PATH/$(basename $tsproj).md;
        echo "-------------------" >> $DOCS_SOURCE_PATH/$(basename $tsproj).md;
        echo '```' >> $DOCS_SOURCE_PATH/$(basename $tsproj).md;
        pytmc pragmalint --verbose "$tsproj" >> $DOCS_SOURCE_PATH/$(basename $tsproj).md 2>&1;
        echo '```' >> $DOCS_SOURCE_PATH/$(basename $tsproj).md;
    done

find $TWINCAT_PROJECT_ROOT -name '*.tmc' -print0 |
    while IFS= read -r -d '' tmc; do
        db_filename=$DOCS_SOURCE_PATH/$(basename $tmc).db
        db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>$db_filename) 2>&1)
        md_filename=$DOCS_SOURCE_PATH/$(basename $tmc).md

        (
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
        ) > $md_filename
    done

pushd $DOCS_PATH
make html
popd

# Deploy the latest version of the docs with doctr
pip install doctr
doctr deploy . --built-docs docs/build/html --deploy-branch-name gh-pages --command "touch .nojekyll; git add .nojekyll" --no-require-master
