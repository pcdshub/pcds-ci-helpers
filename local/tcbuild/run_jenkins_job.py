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
        sln = next(Path(".").glob("*.sln")).resolve()
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
        cmd.extend(("-r", "-a", "172.21.148.95.1.1", "-l", "TwinCAT RT (x64)"))
        expected.extend(("activate config", "run tests"))
    if build_library and should_library(sln):
        cmd.extend(("-f", ""))
        expected.append("build library")
        cmd_builds_lib = True
        if not skip_share:
            expected.append("copy libraries to public folder")
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

    This will either be under an Element with the tag "PlaceholderReference"
    or with the tag "LibraryReference". This will have an "Include" attribute
    that contains the text "TcUnit" but might have a more stringent specification,
    and also will have a sub-element with the "Namespace" tag whose value is
    simply "TcUnit".

    The file may have dozens and dozens of such tags.
    """
    sln = Path(sln)
    plcproj = find_plcproj(sln)
    root = get_xml_root(plcproj)
    libs = root.findall(".//LibraryReference", root.nsmap)
    refs = root.findall(".//PlaceholderReference", root.nsmap)
    for elem in libs + refs:
        if elem.find("Namespace", elem.nsmap).text == "TcUnit":
            logger.debug(f"Found TcUnit reference in xml element {elem}")
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
    title = get_xml_value(plcproj, ["PropertyGroup", "Title"])
    company = get_xml_value(plcproj, ["PropertyGroup", "Company"])
    version = get_xml_value(plcproj, ["PropertyGroup", "ProjectVersion"])
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


@functools.lru_cache(maxsize=5)
def find_plcproj(sln: str | Path) -> Path:
    """
    Returns the path of the .plcproj file.
    """
    sln = Path(sln)
    tsproj = find_tsproj(sln)
    paths = get_xml_attributes(tsproj, ["Project", "Plc", "Project"])
    try:
        # Typically stored in the xti file via reference here
        xti_name = paths["File"]
    except KeyError:
        # Misconfigured: stored right in this file
        logger.debug(f"Getting plcproj from tsproj file {tsproj}")
        plcproj_path = paths["PrjFilePath"]
        plcproj = (tsproj.parent / plcproj_path).resolve()
    else:
        # Implicitly, the xti file is in the _Config/PLC folder
        xti = tsproj.parent / "_Config" / "PLC" / xti_name
        logger.debug(f"Getting plcproj from xti file {xti}")
        plcproj_path = get_xml_attributes(xti, ["Project"])["PrjFilePath"]
        plcproj = (xti.parent / plcproj_path).resolve()
    logger.debug(f"Found plcproj path {plcproj}")
    return plcproj


@functools.lru_cache(maxsize=5)
def find_tsproj(sln: str | Path) -> Path:
    """
    Returns the path of the .tsproj file.
    """
    sln = Path(sln)
    regex = re.compile(r',\s*"(.*\.tsproj)"')
    with sln.open("r") as fd:
        for line in fd.read().splitlines():
            match = regex.search(line)
            if match:
                logger.debug(f"Found tsproj match on line {line.strip()}")
                return sln.parent / match.group(1)
    raise RuntimeError("Did not find tsproj reference in sln")


def get_xml_value(xml_file: str | Path, elem_path: list[str]) -> str:
    """
    Given an xml file and a list of element tag names, get the element value.
    """
    return get_xml_element(xml_file, elem_path).text


def get_xml_attributes(xml_file: str | Path, elem_path: list[str]) -> dict[str, str]:
    """
    Given an xml file and a list of element tag names, get the element attributes.
    """
    return get_xml_element(xml_file, elem_path).attrib


def get_xml_element(xml_file: str | Path, elem_path: list[str]) -> etree.Element:
    """
    Given an xml file and a list of element tag names, get the element.

    Once you have the element, use:
    - element.get to check the attributes
    - element.text to check the value
    - element.find or iterate through the element to find more sub-elements
    """
    elem = get_xml_root(xml_file)
    for path in elem_path:
        elem = elem.find(path, elem.nsmap)
        if elem is None:
            raise RuntimeError(f"Did not find {path} in {elem} while parsing {xml_file}")
    return elem


def get_xml_root(xml_file: str | Path) -> etree.Element:
    """
    Helper function to get the root element of an xml file.
    """
    return _get_xml_root(str(xml_file))


@functools.lru_cache(maxsize=5)
def _get_xml_root(xml_file: str) -> etree.Element:
    """
    Cache the results of the xml loading to avoid extra file operations.
    """
    return etree.parse(xml_file).getroot()


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
