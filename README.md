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
version: ~> 1.0

env:
  global:
    # doctr generated secure variable for documentation upload
    - secure: "<your secure here>"
    # enable the usage of versions menu which allow versioning of the docs
    # pages and not only the master branch
    - DOCTR_VERSIONS_MENU="1"
    # Dependency files used to build the documentation (space separated)
    - DOCS_REQUIREMENTS="dev-requirements.txt requirements.txt"
    # Options to be passed to flake8 for package linting. Usually this is just
    # the package name but you can enable other flake8 options via this config
    - PYTHON_LINT_OPTIONS="my_package"

    # The name of the conda package
    - CONDA_PACKAGE="my_package"
    # The folder containing the conda recipe (meta.yaml)
    - CONDA_RECIPE_FOLDER="conda-recipe"
    # Extra dependencies needed to run the tests which are not included
    # in the recipe or CONDA_REQUIREMENTS. E.g. PyQt
    - CONDA_EXTRAS="pip pyqt=5 happi"
    # Requirements file with contents for tests dependencies
    - CONDA_REQUIREMENTS="dev-requirements.txt"

    # Extra dependencies needed to run the test with Pip (similar to
    # CONDA_EXTRAS) but for pip
    - PIP_EXTRAS="PyQt5 happi"

jobs:
  allow_failures:
    # This makes the PIP based Python 3.6 optional for passing.
    # Remove this block if passing tests with PIP is mandatory for your
    # package
    - name: "Python 3.6 - PIP"

import:
  # If your project requires X11 leave the following import
  - pcdshub/pcds-ci-helpers:travis/shared_configs/setup-env-ui.yml
  # This import enables a set of standard python jobs including:
  # - Build
  #   - Anaconda Package Build
  # - Tests
  #   - Linter
  #   - Documentation
  #   - Python 3.6 - PIP based
  #   - Python 3.6, 3.7 & 3.8 - Conda base
  # - Deploy
  #   - Documentation using doctr
  #   - Conda Package - uploaded to pcds-dev and pcds-tag
  #   - PyPI
  - pcdshub/pcds-ci-helpers:travis/shared_configs/standard-python-conda.yml

# If not using the standard-python-conda above please uncomment the required
# (language, os, dist and stages) and optional (import statements) entries from
# the blocks below.
#
#language: python
#os: linux
#dist: xenial
#
#stages:
#  - build
#  - test
#  - name: deploy
#    if: (branch = master OR tag IS present) AND type != pull_request
#
#import:
#  # Build Stage
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/anaconda-build.yml
#  # Tests Stage
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester-pip.yml
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester-conda.yml
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-linter.yml
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/docs-build.yml
#  # Deploy Stage
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/pypi-upload.yml
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/doctr-upload.yml
#  - pcdshub/pcds-ci-helpers:travis/shared_configs/anaconda-upload.yml
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
PYTHON_LINT_OPTIONS="path/to/source --verbose"
./python_linter.sh
```

`PYTHON_LINT_OPTIONS` can be set to include directory names and/or other flake8
command line options. Any directory names will be relative to the repository's
root directory.


# Travis-CI Shared Configurations

## Standard Configurations
The standard configurations below were created to provide uniformity and make
it easier to use with the PCDS projects.

### shared_configs/standard-python-conda.yml
This import enables a set of standard python jobs including:
- Build Stage
   - Anaconda Package Build
- Tests Stage
  - Linter
   - Documentation
   - Python 3.6 - PIP based
   - Python 3.6, 3.7 & 3.8 - Conda base
 - Deploy Stage
   - Documentation using doctr
   - Conda Package - uploaded to pcds-dev and pcds-tag
   - PyPI

#### usage:
```yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/standard-python-conda.yml
```

### shared_configs/setup-env-ui.yml
This configuration installs `xvfb` and `herbstluftwm` so UI tests can have the
proper behavior.

#### usage:
```yaml
import:
  # If your project requires X11 leave the following import
  - pcdshub/pcds-ci-helpers:travis/shared_configs/setup-env-ui.yml
```

## Building Blocks

If the standard configuration above does not meet your requirements you can
build your own by using a combination of the following pieces below.

### Build Jobs

#### shared_configs/anaconda-build.yml
`anaconda-build.yml` builds a conda package and provides a `workspace` called
`conda` which contains the output of the build process.

##### arguments:
`CONDA_RECIPE_FOLDER` must be set to the folder containing the `meta.yaml` file
of this package recipe.

##### usage:
This configuration can be added by importing it in your `.travis.yml`:
```yaml
  global:
    # The folder containing the conda recipe (meta.yaml)
    - CONDA_RECIPE_FOLDER="conda-recipe"

import:
  - pcdshub/pcds-ci-helpers:travis/shared_config/anaconda-build.yml
```

### Test Jobs

#### shared_configs/python-linter.yml
`python-linter.yml` examines Python code using flake8.

##### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-linter.yml
```
##### arguments:
`PYTHON_LINT_OPTIONS` can be set to include directory names and/or other flake8
command line options. Any directory names will be relative to the repository's
root directory. For example:
``` yaml
env:
  global:
    - PYTHON_LINT_OPTIONS="source --verbose"
```

#### shared_configs/python-tester-conda.yml
`python-tester-conda.yml` runs any pytest tests it finds after installing the
specified requirements via conda.
The current test matrix includes Python 3.6, 3.7 and 3.8.
This job uses the workspace named `conda` for access to the `noarch`
package previously built by the `anaconda-build.yml`, and thus must be
used in conjuction with `anaconda-build.yml`.

##### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester-conda.yml
```
##### arguments:
Test requirements files can be specified by assigning values to
`CONDA_REQUIREMENTS`, which defaults to `dev-requirements.txt`.
If no requirements are necessary, the file can be blank.
Additional test dependencies can be specified via the `CONDA_EXTRAS` variable.
The package name must be defined using the `CONDA_PACKAGE` variable.

Additional dependencies not specified in the requirements files can be
passed to the install process via the `PIP_EXTRAS` variable.

``` yaml
env:
  global:
    # The name of the conda package
    - CONDA_PACKAGE="my_package"
    # The folder containing the conda recipe (meta.yaml)
    - CONDA_RECIPE_FOLDER="conda-recipe"
    # Extra dependencies needed to run the tests which are not included
    # at the recipe and dev-requirements.txt. E.g. PyQt
    - CONDA_EXTRAS="pip pyqt=5 happi"
    # Requirements file with contents for tests dependencies
    - CONDA_REQUIREMENTS="dev-requirements.txt"
```

#### shared_configs/python-tester-pip.yml
`python-tester-pip.yml` runs any pytest tests it finds after installing the
specified requirements via PIP using Python 3.6.

##### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/python-tester-pip.yml
```
##### arguments:
Requirements files can be specified by assigning values to `REQUIREMENTS` and
`DEV_REQUIREMENTS`. `REQUIREMENTS` defaults to `requirements.txt` and
`DEV_REQUIREMENTS` defaults to `dev-requirements.txt`. If no requirements are
necessary, these files can be blank.

Additional dependencies not specified at the requirements files above can be
passed to the install process via the `PIP_EXTRAS` variable.

``` yaml
env:
  global:
    - REQUIREMENTS: requirements.txt
    - DEV_REQUIREMENTS: dev-requirements.txt
    - PIP_EXTRAS="PyQt5 happi"
```

#### shared_configs/docs-build.yml
`docs-build.yml` runs through the build of the package's documentation to
ensure it works properly.
After building the documentation it is available via the workspace named
`docs` which is used by the `doctr-upload.yml` later on for upload.
As of now, the docs build task uses a conda environment since not all of our
dependencies are available through PIP. This can be revisited in the future
once the packages are correctly available.

##### usage:
This configuration can be added to the `test` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/docs-build.yml
```

##### arguments:
- One or more docs requirements file can be specified by assigning a value to
  `DOCS_REQUIREMENTS`, which defaults to `docs-requirements.txt`.
- The folder containing the documentation can be specified by assigning a value
  to `DOCS_FOLDER`, which defaults to `docs`.
``` yaml
env:
  global:
    - DOCS_REQUIREMENTS="dev-requirements.txt requirements.txt"
    - DOCS_FOLDER: docs
    - CONDA_EXTRAS="pip pyqt=5 happi"
```


### Deploy Jobs

#### shared_configs/anaconda-upload.yml
`anaconda-upload.yml` uses the workspace named `conda` to leverage the
pre-built package and speed up the upload task. Thus, this script must be
used in conjunction with `python-tester-conda.yml`
This task uploads the package to the `pcds-dev` channel on Anaconda Cloud.
If the build was triggered by a tag, the package will additionally be uploaded
to the `pcds-tag` channel.

##### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/anaconda-upload.yml
```
##### arguments:
This configuration will only run if `CONDA_UPLOAD_TOKEN_DEV` is defined. This
token can be obtained from anaconda.org by anyone with write permissions to
the `pcds-dev` organization. It should then be added to the Travis build from
the Environment Variables section of the repository's setting on travis-ci.org.
To upload to `pcds-tag`, the same must be done with `CONDA_UPLOAD_TOKEN_TAG`.

#### shared_configs/doctr-upload.yml
`doctr-upload.yml` uploads the package documentation to GitHub Pages using
`Doctr`.

##### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/doctr-upload.yml
```

##### arguments:
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
    - DOCTR_VERSIONS_MENU: 1
```

#### shared_configs/pypi-upload.yml
`pypi-upload.yml` builds the package according to the `setup.py` file and
uploads it to the PyPI. This is only performed on tagged builds.

##### usage:
This configuration can be added to the `deploy` stage of a Travis build by
importing it in your `.travis.yml`:
``` yaml
import:
  - pcdshub/pcds-ci-helpers:travis/shared_configs/pypi-upload.yml
```
##### arguments:
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
