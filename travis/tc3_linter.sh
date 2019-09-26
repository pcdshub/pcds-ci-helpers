# tc3linter.sh 
#
# Intended for :
#
#   language: python
#   dist: xenial
#   python: 3.7

# install pytmc:
pip install Jinja2 lxml
pip install git+https://github.com/slaclab/pytmc.git@v2.1.0
pip install git+https://github.com/epicsdeb/pypdb.git

# install docs
pip install sphinx recommonmark

# Allow user to configure path for documentation drop site 
DEFAULT_DOCS_PATH="docs/source"

if [ -z $1 ]; then
    DOCS_PATH=$DEFAULT_DOCS_PATH
else
    DOCS_PATH=$1
fi

# Execute linting script:
find plc -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        pytmc pragmalint --verbose "$tsproj";
        pytmc summary --all --code "$tsproj" > $DOCS_PATH/$(basename $tsproj).md;
    done


find plc -name '*.tmc' -print0 |
    while IFS= read -r -d '' tmc; do
        db_filename=$DOCS_PATH/$(basename $tmc).db
        db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>$db_filename) 2>&1)
        md_filename=$DOCS_PATH/$(basename $tmc).md

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

pushd docs
make html
popd

# Deploy the latest version of the docs with doctr
pip install doctr
doctr deploy . --built-docs docs/build/html --deploy-branch-name gh-pages --command "touch .nojekyll; git add .nojekyll" --no-require-master
