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
import functools
import logging
import re
import subprocess

from lxml import etree
from pathlib import Path


logger = logging.getLogger(__name__)


def main(
    skip_static: bool = False,
    skip_tests: bool = False,
    build_library: bool = False,
    skip_share: bool = False,
    passthrough: list | None = None,
    dry_run: bool = False,
) -> int:
    """
    Call the other functions to determine what TcBuild command to run.
    """
    try:
        sln = next(Path(".").glob("*.sln"))
    except StopIteration:
        raise RuntimeError("Did not find sln file!")
    # Base command always builds the project with a 5 minute timeout
    cmd = ["TcBuild", "-v", str(sln), "-u", "5"]
    expected = ["build the project"]
    if not skip_static and should_static_analysis(sln):
        cmd.append("-s")
        expected.insert(0, "run static analysis")
    if not skip_tests and should_unit_test(sln):
        # Running the tests requires a target PLC and specification of arch
        cmd.extend(("-r", "-a", "172.21.148.95.1.1", "-l", "'TwinCAT RT (x64)'"))
        expected.extend(("activate config", "run tests"))
    if build_library and should_library(sln):
        cmd.extend(("-f", ""))
        expected.append("build library")
        cmd_builds_lib = True
    else:
        cmd_builds_lib = False
    if passthrough is not None:
        # Inject any additional args needed
        cmd.extend(passthrough)
    logger.info("Command to run: " + " ".join(cmd))
    steps = "\n- ".join([""] + expected)
    logger.info(f"Expected steps: {steps}")
    if dry_run:
        logger.info("Dry-run: exiting")
        return 0
    else:
        rval = subprocess.run(cmd, universal_newlines=True).returncode
        if cmd_builds_lib and rval == 0 and not skip_share:
            return subprocess.run(str(Path(__file__).parent / "share_twincat_libs.bat"))
        else:
            return rval


def should_static_analysis(sln: str | Path) -> bool:
    """
    Returns true if this solution has a static analysis config.

    Static analysis configs are files located in the repo root with this name:
    static-analysis-rules.csa
    """
    sln = Path(sln)
    return (sln.parent / "static-analysis-rules.csa").exists()


def should_unit_test(sln: str | Path) -> bool:
    """
    Returns true if this solution has unit tests.

    As a proxy for this, we'll see if TcUnit is used in the project.
    This information is included in the plcproj file.

    We can search randomly for the plcproj file, but this could cause problems
    if there are multiple projects. Instead we can parse the sln to find the
    tsproj and parse the tsproj to find the plcproj.

    I'm using regex instead of xml parsing because xml parsing is annoying
    when I just need to find a single string.
    """
    sln = Path(sln)
    plcproj = find_plcproj(sln)
    regex = re.compile('PlaceholderReference\s.*Include="TcUnit"')
    with plcproj.open("r") as fd:
        for line in fd.read().splitlines():
            if regex.search(line):
                logger.debug(f"Found TcUnit reference in line {line.strip()}")
                return True
    logger.debug("Found no references to TcUnit in plcproj file")
    return False


def should_library(sln: str | Path) -> bool:
    """
    Returns true if this solution has a version
    and that version is not already installed.
    """
    sln = Path(sln)
    plcproj = find_plcproj(sln)
    tree: etree.ElementTree = etree.parse(str(plcproj))
    title = None
    company = None
    version = None
    for node in tree.getroot():
        if is_matching_node(node, "PropertyGroup"):
            for prop in node:
                if is_matching_node(prop, "Title"):
                    title = prop.text
                if is_matching_node(prop, "Company"):
                    company = prop.text
                if is_matching_node(prop, "ProjectVersion"):
                    version = prop.text
            break
    if None in (title, company, version):
        raise RuntimeError("Did not find matching data in plcproj!")
    # First: check if there's a valid version
    # Version should be of the form e.g. "0.0.0" or "1.2.3"
    version_tuple = tuple(int(text) for text in version.split("."))
    if len(version_tuple) != 3:
        raise RuntimeError(f"Invalid version. Expected 3 numbers, got {version}")
    if version_tuple <= (0, 0, 0):
        # Don't make libraries for dev 0, 0, 0 or weird stuff like -1, 0, 0
        logger.debug(f"Found dev or invalid version {version}")
        return False
    install_path = Path(r"C:\TwinCAT\3.1\Components\Plc\Managed Libraries")
    this_version_path = install_path / company / title / version
    logger.debug(f"Checking path {this_version_path}")
    # Only make library if not already installed
    return not this_version_path.exists()


def is_matching_node(node: etree._Element, key: str) -> bool:
    """
    Return True if the xml element matches the key, or False otherwise.

    These can parse somewhat unexpectedly, with tags like:
    {http://schemas.microsoft.com/developer/msbuild/2003}PropertyGroup

    This happens because of the xmlns (xml namespace) attribute,
    which is set to the url enclosed in brackets in the example above,
    so we can't do a simple node.tag == key check and finding child
    nodes by tag is a chore.

    This helper function is used to iterate through the nodes to find
    the one that matches in these cases.
    """
    if not isinstance(node.tag, str):
        return False
    return node.tag == key or node.tag.endswith(f"}}{key}")


@functools.lru_cache(maxsize=5)
def find_plcproj(sln: str | Path) -> Path:
    """
    Returns the path of the .plcproj file.
    """
    sln = Path(sln)
    tsproj = find_tsproj(sln)
    regex = re.compile('PrjFilePath="(.*\.plcproj)"')
    with tsproj.open("r") as fd:
        for line in fd.read().splitlines():
            match = regex.search(line)
            if match:
                logger.debug(f"Found plcproj on line {line.strip()}")
                return tsproj.parent / match.group(1)
    raise RuntimeError("Did not find plcproj reference in tsproj")


@functools.lru_cache(maxsize=5)
def find_tsproj(sln: str | Path) -> Path:
    """
    Returns the path of the .tsproj file.
    """
    sln = Path(sln)
    regex = re.compile(',\s*"(.*\.tsproj)"')
    with sln.open("r") as fd:
        for line in fd.read().splitlines():
            match = regex.search(line)
            if match:
                logger.debug(f"Found tsproj match on line {line.strip()}")
                return sln.parent / match.group(1)
    raise RuntimeError("Did not find tsproj reference in sln")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-static", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--build-lib", action="store_true")
    parser.add_argument("--skip-share", action="store_true")
    parser.add_argument("--passthrough")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    if args.passthrough is None:
        passthrough = None
    else:
        passthrough = args.passthrough.split()
    exit(
        main(
            skip_static=args.skip_static,
            skip_tests=args.skip_tests,
            build_library=args.build_lib,
            skip_share=args.skip_share,
            passthrough=passthrough,
            dry_run=args.dry_run,
        )
    )
