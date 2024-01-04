"""
Run TcBuild as appropriate based on the situation.

This is expected to be run in the top-level directory of the TwinCAT repo,
and we expect to find .sln files there.

Quick background:

In these Jenkins builds, we have various kinds of libraries and various
kinds of actions we can perform on them.

Our available actions are:
- Static analysis
- Build TwinCAT project
- Activate config
- Run unit test
- Save and install library

We generally want to do all the steps that the project is set up for.
Some caveats:
- We'll only run "save and install library" when there is a new library to build,
  because we want to avoid automatically clobbering existing library files.
- Library needs to be opt-in because we can't automatically tell if a project is
  meant to be a library.
- We need to be able to opt-out of most steps just in case
- We'll probably directly pass through some of the tcbuild options
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def should_static_analysis(sln: str | Path) -> bool:
    """
    Returns true if this solution has a static analysis config.
    """
    sln = Path(sln)
    raise NotImplementedError()


def should_unit_test(sln: str | Path) -> bool:
    """
    Returns true if this solution has unit tests.
    """
    sln = Path(sln)
    raise NotImplementedError()


def should_library(sln: str | Path) -> bool:
    """
    Returns true if this solution has a version
    and that version is not already installed.
    """
    sln = Path(sln)
    raise NotImplementedError()

def main(
    skip_static: bool = False,
    skip_tests: bool = False,
    build_library: bool = False,
    passthrough: list | None = None,
) -> int:
    """
    Call the other functions to determine what TcBuild command to run.
    """
    try:
        sln = Path(".").glob("*.sln")[0]
    except IndexError:
        raise RuntimeError("Did not find sln file!")
    # Base command always builds the project with a 5 minute timeout
    cmd = ["TcBuild", "-v", str(sln), "-u", "5"]
    if not skip_static and should_static_analysis(sln):
        cmd.append("-s")
    if not skip_tests and should_unit_test(sln):
        # Running the tests requires a target PLC and specification of arch
        cmd.extend(("-r", "-a", "172.21.148.95.1.1", "-l", "'TwinCAT RT (x64)'"))
    if build_library and should_library(sln):
        cmd.extend(("-f", ""))
    if passthrough is not None:
        # Inject any additional args needed
        cmd.extend(passthrough)
    return subprocess.run(cmd, universal_newlines=True).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-static", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--build-lib", action="store_true")
    parser.add_argument("--passthrough")
    args = parser.parse_args()
    if args.passthrough is None:
        passthrough = None
    else:
        passthrough = args.passthrough.split()
    exit(
        main(
            skip_static=args.skip_static,
            skip_tests=args.skip_tests,
            build_library=args.build_lib,
            passthrough=passthrough,
        )
    )
