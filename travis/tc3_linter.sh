#!/bin/bash

# tc3linter.sh 

LINTER_PYTHON_VERSION=3.7

# Install conda and configure an environemnt if one is not detected

if [ -z $CONDA_DEFAULT_ENV]; then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    conda config --set always_yes yes --set changeps1 no
    conda install conda-build anaconda-client
    conda update -q conda conda-build
    conda config --add channels pcds-tag
    conda config --append channels conda-forge
    # Useful for debugging
    conda info -a
    # Manage conda environment
    conda create -n tc3_linter-env python=$LINTER_PYTHON_VERSION pytmc pip
    source activate tc3_linter-env
else
    # just install pytmc:
    pip install Jinja2 lxml
    pip install git+https://github.com/slaclab/pytmc.git@v2.1.0
    pip install git+https://github.com/epicsdeb/pypdb.git
fi

# install docs
pip install sphinx recommonmark

# Allow user to configure path for documentation drop site 
DEFAULT_DOCS_PATH="docs"
DEFAULT_DOCS_SOURCE_PATH="docs/source"

echo "PYTMC cersion:"
echo $(pytmc --version)

if [ -z $1 ]; then
    DOCS_SOURCE_PATH=$DEFAULT_DOCS_SOURCE_PATH
    DOCS_PATH=$DEFAULT_DOCS_PATH
else
    DOCS_SOURCE_PATH=$1
    DOCS_PATH=$2
fi
   



mkdir -p $DOCS_SOURCE_PATH

# Execute linting script:
find . -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        pytmc pragmalint --verbose "$tsproj";
        pytmc summary --all --code "$tsproj" > $DOCS_SOURCE_PATH/$(basename $tsproj).md;
    done


find . -name '*.tmc' -print0 |
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
