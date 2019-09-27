pcds-ci-helpers
===============
This repository is a place to store complex scripts for continuous integration that may see common use.

You can use the tools in this script with the following commands:

```yaml
install:
  # Import the helper scripts
  - git clone --depth 1 git://github.com/pcdshub/pcds-ci-helpers.git
  # Call the script of your choice
  - bash pcds-ci-helpers/traivs/tc3_linter.sh
```

Documentation
-------------
### travis

#### tc3_linter.sh
tc3_linter.sh examines TwinCAT3 and publishes a sphinx-compatible set of pages summarizing the TwinCAT3 project and the IOC it will generate. This is ideal for assessing [PYTMC](https://github.com/slaclab/pytmc) dependent TwinCAT3 projects. This script functions well in conjunction with [doctr](https://pypi.org/project/doctr/) for build reports. For usage with doctr, you will need to initialize doctr, provide a deployment key, and enable github pages independently.

##### usage:
```sh
> bash pcds-ci-helpers/traivs/tc3_linter.sh [docs_deploy_path]
```
##### arguments:
```bash
docs_deploy_path:
  The location where the build documentation will be placed. This defaults to 'docs/source'
```

References
----------
The architecture of this repository is inspired by [astropy/ci-helpers](https://github.com/astropy/ci-helpers).
