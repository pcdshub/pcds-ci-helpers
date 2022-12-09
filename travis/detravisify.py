#!/usr/bin/env python3
"""
Travis configuration to a standalone script
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Union, Optional

import apischema
import yaml


class Script(str):
    ...


def _empty_script() -> Script:
    return Script("")


@apischema.deserializer
def _(value: Union[str, list[str]]) -> Script:
    if not isinstance(value, str):
        value = "\n".join(value)

    return Script(value)

def env_to_exports(env_list: Union[list[dict[str, str]], dict[str, str]]) -> list[str]:
    res = []
    if isinstance(env_list, dict):
        env_list = [env_list]
    for env in env_list:
        for var, value in env.items():
            res.append(f'export {var}="{value}"')
    return res


@dataclass
class Workspace:
    create: dict[str, Any] = field(default_factory=dict)
    use: Union[str, list[str]] = ""


@dataclass
class Job:
    stage: str = ""
    name: str = ""
    python: Union[float, str] = ""
    env: list[dict[str, Union[str, int, float]]] = field(default_factory=list)
    workspaces: Optional[Workspace] = None
    before_install: Script = field(default_factory=_empty_script)
    install: Script = field(default_factory=_empty_script)
    before_script: Script = field(default_factory=_empty_script)
    script: Script = field(default_factory=_empty_script)

    before_deploy: Script = field(default_factory=_empty_script)
    # TODO: apischema bug? 
    # on: tags: true becomes -> True: {'tags': True}}
    deploy: Optional[dict] = None
    after_deploy: Script = field(default_factory=_empty_script)

    after_script: Script = field(default_factory=_empty_script)
    after_success: Script = field(default_factory=_empty_script)
    after_failure: Script = field(default_factory=_empty_script)
    if_: str = field(default="", metadata=apischema.metadata.alias(arg="if"))

    def to_script(self) -> str:
        result = [
            f"# Job: {self.name} (stage: {self.stage})",
        ]
        
        def add_if_set(desc: str, lines: str):
            if not lines:
                return
            if result:
                result.append("")
            result.append(f"# {desc}")
            if lines in ("skip", ):
                result.append("# (Skipped)")
            else:
                result.extend(lines.splitlines())

        if self.env:
            add_if_set("Environment settings:", "\n".join(env_to_exports(self.env)))

        # Ref: https://docs.travis-ci.com/user/job-lifecycle/
        add_if_set("Before install:", self.before_install)
        add_if_set("Install:", self.install)

        add_if_set("Before script:", self.before_script)
        add_if_set("Script:", self.script)

        add_if_set("Before deploy:", self.before_deploy)
        if self.deploy is not None:
            add_if_set("Deploy:", str(self.deploy))
        add_if_set("After deploy:", self.after_deploy)

        add_if_set("After script:", self.after_script)
        add_if_set("After success:", self.after_success)
        add_if_set("After failure:", self.after_failure)
        return "\n".join(result)


@dataclass
class Jobs:
    include: list[Job] = field(default_factory=list)
    exclude: list[Job] = field(default_factory=list)
    allow_failures: Union[bool, list[dict[str, str]]] = False
    fast_finish: bool = False

    def to_script(self) -> str:
        return "\n\n".join(
            include.to_script() for include in self.include
        )


def detravisify(contents: str) -> str:
    conf = yaml.load(contents, Loader=yaml.Loader)
    if "jobs" not in conf:
        print("No jobs in Travis configuration", file=sys.stderr)
        return ""

    jobs = apischema.deserialize(Jobs, conf["jobs"])

    result = []
    for job in jobs.include:
        result.append(job.to_script())

    return "\n".join(result)


def main(fn: str):
    with open(fn) as fp:
        contents = fp.read()

    print(detravisify(contents))


if __name__ == "__main__":
    fn = sys.argv[1]
    main(fn)
