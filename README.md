pcds-ci-helpers
===============
This repository is a place to store complex scripts for continuous integration
that may see common use.

For TwinCAT projects, you can use the tools in this script with the following
commands:

```yaml
matrix:
  include:
    - name: Project summary
      python: 3.7
      env: TWINCAT_SUMMARY=1
    - name: Pragma linting
      python: 3.7
      env: TWINCAT_PRAGMALINT=1
    - name: Documentation building
      python: 3.7
      env: TWINCAT_BUILD_DOCS=1
    - name: Twincat Style
      python: 3.7
      env: TWINCAT_STYLE=1
    - name: Pre-commit Checks
      python: 3.7
      env: PRE_COMMIT=1

install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  # Start the helper-script initialization + run based on environment variables
  - source pcds-ci-helpers/travis/init.sh
```


For Python projects, you can use the tools in this script with the following
commands:

```yaml
stages:
  - test
  - name: deploy
    if: (branch = master OR tag IS present) AND type != pull_request

import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-linter.yml
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester.yml
  - pcdshub/pcds-ci-helpers:travis/shared_configs/pypi-upload.yml
  - pcdshub/pcds-ci-helpers:travis/shared_configs/doctr-upload.yml
  - pcdshub/pcds-ci-helpers:travis/shared_configs/anaconda-upload.yml
```


Documentation
-------------

### init.sh
`init.sh` acts as a general-purpose initialization hook on Travis CI.  It
allows for various tasks to be run during the `install` phase. While this
script supports Python linting, it is recommended to use
`shared_configs/python-linter.yml` instead.

Currently, it supports:
* TwinCAT3 project summary (see `tc3_summary.sh`)
* TwinCAT3 project pytmc linting (see `tc3_pragmalint.sh`)
* TwinCAT3 documentation building (see `tc3_linter.sh`)
* Python linting via flake8 (see `python_linter.sh`)

This script must be sourced for each of the above features:

```
install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  - source pcds-ci-helpers/travis/init.sh
```

### tc3_linter.sh
`tc3_linter.sh` examines TwinCAT3 and publishes a sphinx-compatible set of
pages summarizing the TwinCAT3 project and the IOC it will generate. This is
ideal for assessing [PYTMC](https://github.com/slaclab/pytmc) dependent
TwinCAT3 projects. This script functions well in conjunction with
[Doctr](https://pypi.org/project/doctr/) for build reports. For usage with
Doctr, you will need to initialize Doctr, provide a deployment key, and enable
GitHub Pages independently.

#### usage:
```sh
> bash pcds-ci-helpers/travis/tc3_linter.sh [docs_deploy_path]
```
#### arguments:
`docs_deploy_path`:
The location where the build documentation will be placed. This defaults to
'docs/source'

### tc3_summary.sh
`tc3_summary.sh` provides a project summary for all TwinCAT3 projects.

#### usage:
The suggested usage is with a separate summary-only step using `init.sh`.

`.travis.yml`
```yaml
matrix:
  include:
    - name: Project summary
      python: 3.7
      env: TWINCAT_SUMMARY=1
```

`TWINCAT_PROJECT_ROOT` may be specified here, defaulting to
`$TRAVIS_BUILD_DIR`.

### tc3_pragmalint.sh
`tc3_pragmalint.sh` performs pragma linting on all TwinCAT3 projects.

#### usage:
The suggested usage is with a separate summary-only step using `init.sh`.

`.travis.yml`
```yaml
matrix:
  include:
    - name: Pragma lint
      python: 3.7
      env: TWINCAT_PRAGMALINT=1
```

`TWINCAT_PROJECT_ROOT` may be specified here, defaulting to
`$TRAVIS_BUILD_DIR`.

### python_linter.sh
`python_linter.sh` lints given Python package(s) with the provided flake8
arguments.

#### usage:
This script is left here for use in local tests. To test locally, simply run
the script from the command line. If you wish to specify linter options, set
`PYTHON_LINT_OPTIONS` beforehand. If you wish to run a Python linter in Travis,
it is recommended to instead use `shared_configs/python-linter.yml`.
``` bash
PYTHON_LINT_OPTIONS="source --verbose"
./python_linter.sh
```

`PYTHON_LINT_OPTIONS` can be set to include directory names and/or other flake8
command line options. Any directory names will be relative to the repository's
root directory.

### shared_configs/python-linter.yml
`python-linter.yml` examines Python code using flake8.

#### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-linter.yml
```
#### arguments:
`PYTHON_LINT_OPTIONS` can be set to include directory names and/or other flake8
command line options. Any directory names will be relative to the repository's
root directory. For example:
``` yaml
env:
  global:
    - PYTHON_LINT_OPTIONS="source --verbose"
```

### shared_configs/python-tester.yml
`python-tester.yml` runs any pytest tests it finds after installing the
specified requirements.

#### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester.yml
```
#### arguments:
Requirements files can be specified by assigning values to `REQUIREMENTS` and
`DEV_REQUIREMENTS`. `REQUIREMENTS` defaults to `requirements.txt` and
`DEV_REQUIREMENTS` defaults to `dev-requirements.txt`. If no requirements are
necessary, the file can be blank.
``` yaml
env:
  global:
    - REQUIREMENTS: requirements.txt
    - DEV_REQUIREMENTS: dev-requirements.txt
```

### shared_configs/doctr-upload.yml
`docs-build.yml` runs through the build of the package's documentation to
ensure it works properly.

#### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/docs-build.yml
```

#### arguments:
- A docs requirements file can be specified by assigning a value to
  `DOCS_REQUIREMENTS`, which defaults to `docs-requirements.txt`.
- The folder containing the documentation can be specified by assigning a value
  to `DOCS_FOLDER`, which defaults to `docs`.
``` yaml
env:
  global:
    - DOCS_REQUIREMENTS: docs-requirements.txt
    - DOCS_FOLDER: docs
```

### shared_configs/anaconda-upload.yml
`anaconda-upload.yml` builds the package according to the `conda-recipe` and
uploads it to the `pcds-dev` channel on Anaconda Cloud. If the build was
triggered by a tag, the package will additionally be uploaded to the `pcds-tag`
channel.

#### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/anaconda-upload.yml
```
#### arguments:
This configuration will only run if `CONDA_UPLOAD_TOKEN_DEV` is defined. This
token can be obtained from anaconda.org by anyone with write permissions to
the `pcds-dev` organization. It should then be added to the Travis build from
the Environment Variables section of the repository's setting on travis-ci.org.
To upload to `pcds-tag`, the same must be done with `CONDA_UPLOAD_TOKEN_TAG`.

### shared_configs/doctr-upload.yml
`doctr-upload.yml` builds the package's documentation and uploads it to GitHub
Pages using `Doctr`.

#### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/doctr-upload.yml
```
#### arguments:
- A docs requirements file can be specified by assigning a value to
  `DOCS_REQUIREMENTS`, which defaults to `docs-requirements.txt`.
- The folder containing the documentation can be specified by assigning a value
  to `DOCS_FOLDER`, which defaults to `docs`.
- If you want a version menu to be included in your documentation, assign a `1`
  to `DOCTR_VERSIONS_MENU`.
- To successfully upload the documentation, doctr is going to need a deploy
  key. This key can be generated by anyone with admin permissions to the
  repository. It should then be added to the Travis build as a secure
  environment variable as shown below. For more instructions, please see
  https://drdoctr.github.io/commandline.html#doctr-configure
``` yaml
env:
  global:
    # Doctr deploy key for <org>/<repo>
    - secure: "<docs build key>"
    - DOCS_REQUIREMENTS: docs-requirements.txt
    - DOCS_FOLDER: docs
    - DOCTR_VERSIONS_MENU: 1
```

### shared_configs/pypi-upload.yml
`pypi-upload.yml` builds the package according to the `setup.py` file and
uploads it to the PyPI. This is only performed on tagged builds.

#### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/pypi-upload.yml
```
#### arguments:
The upload will only succeed if `PYPI_TOKEN` is defined. This token can be
obtained from pypi.org by anyone with Maintainer or Owner permissions. It
should then be added to the Travis build from the Environment Variables section
of the repository's setting on travis-ci.org. To upload to `pcds-tag`, the same
must be done with `CONDA_UPLOAD_TOKEN_TAG`.

Examples
--------
See [`example_twincat_travis.yml`](https://github.com/pcdshub/pcds-ci-helpers/blob/master/example_twincat_travis.yml) and [`example_python_travis.yml`](https://github.com/pcdshub/pcds-ci-helpers/blob/master/example_python_travis.yml).

Acknowledgements
----------------
The architecture of this repository is inspired by [astropy/ci-helpers](https://github.com/astropy/ci-helpers).
