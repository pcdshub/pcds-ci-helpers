pcds-ci-helpers
===============
This repository is a place to store complex scripts for continuous integration that may see common use.

For TwinCAT projects, you can use the tools in this script with the following commands:

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

install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  # Start the helper-script initialization + run based on environment variables
  - source pcds-ci-helpers/travis/init.sh
```


For Python projects, you can use the tools in this script with the following commands:

```yaml
matrix:
  include:
    - name: Python linting
      python: 3.7
      env: LINT_PYTHON=pkg_name

install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  # Start the helper-script initialization + run based on environment variables
  - source pcds-ci-helpers/travis/init.sh
```


Documentation
-------------
### travis

#### init.sh
`init.sh` acts as a general-purpose initialization hook on Travis CI.  It
allows for various tasks to be run during the `install` phase.

Currently, it supports:
* Python linting via flake8 (see `python_linter.sh`)
* TwinCAT3 project summary (see `tc3_summary.sh`)
* TwinCAT3 project pytmc linting (see `tc3_pragmalint.sh`)
* TwinCAT3 documentation building (see `tc3_linter.sh`)

This script must be sourced for each of the above features:

```
install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  - source pcds-ci-helpers/travis/init.sh
```

#### tc3_linter.sh
tc3_linter.sh examines TwinCAT3 and publishes a sphinx-compatible set of pages summarizing the TwinCAT3 project and the IOC it will generate. This is ideal for assessing [PYTMC](https://github.com/slaclab/pytmc) dependent TwinCAT3 projects. This script functions well in conjunction with [doctr](https://pypi.org/project/doctr/) for build reports. For usage with doctr, you will need to initialize doctr, provide a deployment key, and enable github pages independently.

##### usage:
```sh
> bash pcds-ci-helpers/travis/tc3_linter.sh [docs_deploy_path]
```
##### arguments:
```bash
docs_deploy_path:
  The location where the build documentation will be placed. This defaults to 'docs/source'
```

#### python_linter.sh
`python_linter.sh` lints given Python package(s) with the provided flake8 arguments.

##### usage:
The suggested usage is with a separate lint-only step using `init.sh`.

`.travis.yml`
```yaml
matrix:
  include:
    - name: flake8 linting
      python: 3.6
      env: LINT_PYTHON=.
```

`LINT_PYTHON` could be set to directory names or include additional flake8
flags.

#### tc3_summary.sh
`tc3_summary.sh` provides a project summary for all TwinCAT3 projects.

##### usage:
The suggested usage is with a separate summary-only step using `init.sh`.

`.travis.yml`
```yaml
matrix:
  include:
    - name: Project summary
      python: 3.7
      env: TWINCAT_SUMMARY=1
```

`TWINCAT_PROJECT_ROOT` may be specified here, defaulting to `$TRAVIS_BUILD_DIR`.

#### tc3_pragmalint.sh
`tc3_pragmalint.sh` performs pragma linting on all TwinCAT3 projects.

##### usage:
The suggested usage is with a separate summary-only step using `init.sh`.

`.travis.yml`
```yaml
matrix:
  include:
    - name: Pragma lint
      python: 3.7
      env: TWINCAT_PRAGMALINT=1
```

`TWINCAT_PROJECT_ROOT` may be specified here, defaulting to `$TRAVIS_BUILD_DIR`.

Examples
--------

See `example_twincat_travis.yml` and `example_python_travis.yml`.

References
----------
The architecture of this repository is inspired by [astropy/ci-helpers](https://github.com/astropy/ci-helpers).
