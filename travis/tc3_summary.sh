#!/bin/bash

source settings.sh
cd $TWINCAT_PROJECT_ROOT

pip install pytmc

# Execute linting script:
find . -name '*.tsproj' -print0 | 
    while IFS= read -r -d '' tsproj; do 
        pytmc summary --all --code --markdown "$tsproj"
    done

exit 0
