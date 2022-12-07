#!/usr/bin/env python3
"""
Travis configuration to a standalone script
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Union

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
class Job:
    stage: str = ""
    name: str = ""
    python: Union[float, str] = ""
    env: list[dict[str, str]] = field(default_factory=list)
    workspaces: dict[str, str] = field(default_factory=dict)
    before_script: Script = field(default_factory=_empty_script)
    install: Script = field(default_factory=_empty_script)
    script: Script = field(default_factory=_empty_script)
    after_failure: Script = field(default_factory=_empty_script)

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
            result.extend(lines.splitlines())

        if self.env:
            add_if_set("Environment settings:", "\n".join(env_to_exports(self.env)))

        add_if_set("Before script:", self.before_script)
        add_if_set("Install:", self.install)
        add_if_set("Script:", self.script)
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
    import pprint
    pprint.pprint(conf["jobs"])
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
