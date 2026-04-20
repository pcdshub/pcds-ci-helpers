# pcds-ci-helpers

This repository is a place to store complex scripts for continuous integration
that may see common use.

## GitHub Actions Standard Workflows

### TwinCAT

For TwinCAT projects, you can use the shared workflows by adding the following file
to your project as ``.github/workflows/standard.yml``:

[example_twincat_gha.yml](example_twincat_gha.yml)

### Python

For Python projects, you can use the shared workflows by adding the following file
to your project as ``.github/workflows/standard.yml``:

[example_python_gha.yml](example_python_gha.yml)

## Local

The local folder includes helper scripts for local ci builds.
Currently, this only includes TwinCAT builds that cannot easily be run on the cloud.

## Travis

The travis folder was original used for travis ci builds, which have since been
discontinued because travis offers an arguably worse product at a higher price point
than github actions.
