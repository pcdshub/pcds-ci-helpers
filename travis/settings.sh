_header() {
    echo ""
    echo "-------------------------------------------------------"
    for line in "$@"
    do
        echo "$line";
    done
    echo "-------------------------------------------------------"
}


export TWINCAT_PROJECT_ROOT=${TWINCAT_PROJECT_ROOT:-$TRAVIS_BUILD_DIR}

if [ -z "$CI_HELPER_PATH" ]; then
    export CI_HELPER_PATH="$TRAVIS_BUILD_DIR/pcds-ci-helpers"
fi
