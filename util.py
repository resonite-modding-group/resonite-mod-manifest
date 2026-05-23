"""
Utils for the other python scripts
"""

import sys
from typing import Any
import subprocess

from packaging.version import Version

def should_show_mod(mod: dict[str, Any]) -> bool:
    """
    Checks if mod should be shown.

    Parameters:
    mod: The mod in question
    """

    # Exclude deprecated and file only 
    if "flags" in mod and (
        "deprecated" in mod["flags"] or
        "file" in mod["flags"]
    ):
        return False

    # Only show mods with versions
    if mod["versions"] is None or len(mod["versions"]) == 0:
        return False

    # # Don't show mods with only vulnerable versions
    # only_vulnerable_versions = True
    # for version in mod["versions"]:
    #     if "flags" not in version:
    #         only_vulnerable_versions = False
    #     else:
    #         if not any(flag.startswith("vulnerability:") for flag in version["flags"]):
    #             only_vulnerable_versions = False

    # if only_vulnerable_versions:
    #     return False

    # Show all mods by default
    return True

def map_mod_versions(versions: dict[str, Any], mod_guid: str) -> list[dict[str, Any]]:
    """
    Filters unwanted mod versions away, and turns them into a list

    Parameters:
    versions: The mod's versions
    mod_guid: The mod's GUID
    """

    versions_list: list[dict[str, Any]] = []
    for version_id in versions:
        try:
            mod_version = versions[version_id]
            mod_version["id"] = Version(version_id)
            # Skip over listing pre-release versions
            if (
                "preRelease" in mod_version or
                mod_version["id"].is_prerelease or
                mod_version["id"].is_devrelease
            ):
                continue
            versions_list.append(mod_version)
        except Exception as err:
            print(
                f"Failed to process [{mod_guid}/{version_id}], reason: {err}",
                file=sys.stderr
            )

    return versions_list


def exec_shell(command: str) -> str:
    """
    Execute a shell command, and throws an exception if it fails, otherwise return the output.

    Parameters:
    command: The command to execute in the system shell
    """
    [status, output] = subprocess.getstatusoutput(command)
    if status != 0:
        raise Exception(f"{command} exited with status ${status}, output: {output}")
    return output

def hex_to_int(s: str) -> int:
    """
    Convert a hex code to an int
    """
    return int(s.lstrip("#"), 16)
