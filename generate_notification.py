# #!/bin/python

"""
Basic JSON diffing between two git versions of the 'manifest.json' file,
When a new version of a mod is found, this will write to GITHUB_OUTPUT with a discord webhook message JSON
"""

import json
import datetime
from os import environ
from copy import deepcopy
from typing import Any

import util

REF_BASE = util.exec_shell(f"git rev-parse {environ.get('REF_BASE') or 'HEAD^1'}")
REF_NEW = util.exec_shell(f"git rev-parse {environ.get('REF_NEW') or 'HEAD'}")
 
OLD_MANIFEST: dict[str, Any] = json.loads(util.exec_shell(f"git show {REF_BASE}:manifest.json"))
NEW_MANIFEST: dict[str, Any] = json.loads(util.exec_shell(f"git show {REF_NEW}:manifest.json"))

# For local testing
# with open("manifest_previous.json","r") as file_previous:
#     OLD_MANIFEST: dict[str, Any] = json.load(file_previous)
# with open("manifest.json","r") as file:
#     NEW_MANIFEST: dict[str, Any] = json.load(file)

EMBEDS = []

BASE_EMBED: dict[str, Any] = {
    "footer": {
        "icon_url": "https://github.com/resonite-modding-group.png"
    },
    "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    "fields": []
}

def mod_to_embed(mod_entry: dict[str, Any], is_new: bool ) -> dict[str, Any]:
    """
    Create discord embed JSON from a mod entry and its newest release
    """
    embed: dict[str, Any] = deepcopy(BASE_EMBED)
    embed['title'] = f"[{mod_entry['name']}/{mod_entry['versions'][0]['id']}]"
    embed['description'] = mod_entry['description']
    author = next(iter(mod_entry['author']))
    embed['footer']['text'] = author
    author_data = mod_entry['author'][author]

    if is_new:
        embed['color'] = util.hex_to_int("#59eb5c")
    else:
        embed['color'] = util.hex_to_int("#236994")

    if 'icon' in author_data:
        embed['footer']['icon_url'] = author_data['icon']
    else:
        embed['footer']['icon_url'] = "https://github.com/resonite-modding-group.png"

    if 'releaseUrl' in mod_entry['versions'][0]:
        embed['url'] = mod_entry['versions'][0]['releaseUrl']

    embed['fields'].append({
        "name": "Category",
        "value": mod_entry['category'],
        "inline": True
    })

    if 'flags' in mod_entry:
        embed['fields'].append({
            "name": "Flags",
            "value": "`" + "`, `".join(mod_entry['flags']) + "`",
            "inline": True
        })

    if 'tags' in mod_entry:
        embed['fields'].append({
            "name": "Tags",
            "value": "`" + "`, `".join(mod_entry['tags']) + "`",
            "inline": True
        })

    links: list[str] = []
    if 'website' in mod_entry:
        links.append("[Website](" + mod_entry['website'] + ")")
    if 'sourceLocation' in mod_entry:
        links.append("[Source](" + mod_entry['sourceLocation'] + ")")
    if links:
        embed['fields'].append({
            "name": "Links",
            "value": ", ".join(links),
            "inline": True
        })

    if 'conflicts' in mod_entry['versions'][0]:
        conflicts: list[str] = []
        for conflict_guid, conflict_data in mod_entry['versions'][0]['conflicts'].items():
            conflicts.append(f"`{conflict_guid}`: {conflict_data['version']}")

        if conflicts:
            embed['fields'].append({
                "name": "Conflicts",
                "value": "- " + "\n- ".join(conflicts),
            })

    if 'dependencies' in mod_entry['versions'][0]:
        dependencies: list[str] = []
        for dep_guid, dep_data in mod_entry['versions'][0]['dependencies'].items():
            dependencies.append(f"`{dep_guid}`: {dep_data['version']}")

        if dependencies:
            embed['fields'].append({
                "name": "Dependencies",
                "value": "- " + "\n- ".join(dependencies),
            })

    if 'changelog' in mod_entry['versions'][0]:
        embed['fields'].append({
            "name": "Changelog",
            "value": mod_entry['versions'][0]['changelog'],
        })

    return embed


for author_guid in NEW_MANIFEST["objects"]:
    entry_data = NEW_MANIFEST["objects"][author_guid]

    # Iterate through each mod entry in the author entry dictionary
    for mod_entry_key, mod_entry_value in entry_data['entries'].items():
        mod_entry_value["versions"] = util.map_mod_versions(mod_entry_value["versions"], author_guid)

        if util.should_show_mod(mod_entry_value):
            # Sort the mod's versions
            mod_entry_value["versions"].sort(reverse=True, key=lambda version: version["id"])
            new_version_to_post = True
            is_new = False

            # if author exists
            if author_guid in OLD_MANIFEST["objects"]:
                # mod key exist
                if mod_entry_key in OLD_MANIFEST["objects"][author_guid]['entries']:
                    old_versions = OLD_MANIFEST["objects"][author_guid]['entries'][mod_entry_key]['versions']
                    old_versions = util.map_mod_versions(old_versions, author_guid)

                    # if the same set of versions exists
                    for version in old_versions:
                        if version['id'] == mod_entry_value["versions"][0]['id']:
                            new_version_to_post = False
                            break
                else:
                    # mod key didn't exist already
                    is_new = True
            else:
                # no author in old, definitely new
                is_new = True

            if new_version_to_post:
                mod_entry_value["author"] = entry_data["author"] #gives the specific mod with an update and copies the author data into it
                EMBEDS.append(mod_to_embed(mod_entry_value, is_new))

if EMBEDS:
    DISCORD_JSON = {
        "embeds": EMBEDS,
        "username": "Resonite Mod Verifications",
        "avatar_url": "https://github.com/resonite-modding-group.png"
    }

    with open(environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"JSON={json.dumps(DISCORD_JSON)}\n")

else:
    print("No changes")
