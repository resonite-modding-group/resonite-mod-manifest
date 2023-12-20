import os
import json

root_folder = "manifest"
manifest = {}

# Store author information so authors can be linked from other entries
author_data = {}

for author_entry in os.scandir(root_folder):
    if(author_entry.is_dir()):
        author_info_path = os.path.join(author_entry.path, "author.json")
        if os.path.exists(author_info_path):
            with open(author_info_path, "r") as author_file:
                author_info = json.load(author_file)
                author_data[author_entry.name] = author_info

# Iterate through the author folders again to build the manifest
for author_entry in os.scandir(root_folder):
    if(author_entry.is_dir()):
        author_info_path = os.path.join(author_entry.path, "author.json")
        if os.path.exists(author_info_path):
            with open(author_info_path, "r") as author_file:
                author_info = json.load(author_file)
                author = author_info["author"]
                manifest[author_entry.name] = {
                    "author": author,
                    "entries": {}
                }
                # Look for all mod entries in the author folder
                entry_folders = [entry.name for entry in os.scandir(author_entry.path) if entry.is_dir()]
                for entry_folder in entry_folders:
                    entry_folder_path = os.path.join(author_entry.path, entry_folder)
                    entry_info_path = os.path.join(entry_folder_path, "info.json")
                    if os.path.exists(entry_info_path):
                        with open(entry_info_path, "r", encoding='utf-8') as entry_file:
                            entry_info = json.load(entry_file)
                            # Process additionalAuthor entries
                            if "additionalAuthors" in entry_info and isinstance(entry_info["additionalAuthors"], list):
                                additional_authors = entry_info["additionalAuthors"]
                                additional_authors_info = {}
                                for author_key in additional_authors:
                                    if author_key in author_data:
                                        additional_author_info = author_data[author_key]["author"]
                                        additional_authors_info[author_key] = additional_author_info
                                    else:
                                        additional_authors_info[author_key] = {}
                                entry_info["additionalAuthors"] = additional_authors_info

                            # Use the mod id as the key for each entry
                            entry_id = entry_info.pop("id", None)
                            manifest[author_entry.name]["entries"][entry_id] = entry_info

# Remove authors with no entries
manifest_part = {author: data for author, data in manifest.items() if data["entries"]}

# Add the schema to the top of the file
manifest = {
    "schemaVersion": "1.0.1",
    "objects": manifest_part
}

# Write the manifest.json
try:
    with open("manifest.json", "w") as manifest_file:
        json.dump(manifest, manifest_file, indent=4, separators=(',', ': '), sort_keys=True)
    print("manifest.json created successfully")
except Exception as e:
    print(f"Error writing manifest.json: {e}")
    exit(1)

