#!/bin/bash
# usage:
#   * create an API token at pypi https://pypi.org/manage/account/ providing
#     access to upload packages for a particular repo or all repos under your
#     account
#   * add a secure variable named PYPI_TOKEN into your Travis-CI
#     settings for the repository
#   * set UPLOAD_PYTHON to be the package name to upload
#   * set UPLOAD_ARGS to be the arguments to setup.py (e.g., sdist)
#   * source `python_pypi_upload.sh` on Travis CI

if [ $TRAVIS ]; then
    cat <<EOF 1>&2
    WARNING: This script has been deprecated.
    Please use the new shared configuration yamls instead.
    Instructions for use can be found in the README.md at:
    https://github.com/pcdshub/pcds-ci-helpers
EOF
fi

if [[ -z "$TRAVIS_TAG" ]]; then
  echo "Skipping PyPI upload as this is not a tag build."
  exit 0
fi

if [["$TRAVIS_BRANCH" -ne "master"]]; then
  echo "Only allowed to upload from the master branch."
  exit 0
fi

if [[ -z "$PYPI_TOKEN" ]]; then
    echo "Skipping PyPI upload as PYPI_TOKEN is undefined at TravisCI"
    exit 0
fi

echo "Installing twine for the upload"
pip install twine

PYPI_PYTHON_PATH=${UPLOAD_PYTHON:-$TRAVIS_BUILD_DIR}
SETUP_ARGS=${BUILD_ARGS:-"sdist"}

cd $PYPI_PYTHON_PATH

echo "Creating the "
python setup.py ${SETUP_ARGS}
twine upload -u __token__ -p ${PYPI_TOKEN} dist/*; TWINE_EXIT_CODE=$?
if [ $TWINE_EXIT_CODE -ne 0 ]; then
    echo "Exit code: $TWINE_EXIT_CODE"
fi

sleep 1.0

exit $TWINE_EXIT_CODE
