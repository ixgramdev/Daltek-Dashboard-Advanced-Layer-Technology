import json
import os


def remove_system_generated(items, module):
    for i in range(len(items) - 1, -1, -1):
        item = items[i]
        if (
            "is_system_generated" in item.keys()
            and item["is_system_generated"]
            or "module" in item.keys()
            and item["module"] != module
        ):
            print("Delete: " + item["name"])
            items.pop(i)
    items.sort(key=lambda k: k["creation"])


def clear_file(file_name):
    file = open(file_name)
    data = json.load(file)
    file.close()

    print("Processing custom fields...")
    remove_system_generated(data["custom_fields"], "Cuba")
    print("Processing property setters...")
    remove_system_generated(data["property_setters"], "Cuba")
    if data["custom_fields"] or data["property_setters"]:
        with open(file_name, "w") as file:
            file.write(json.dumps(data, sort_keys=True, indent=1))
            file.close()
    else:
        os.remove(file_name)


def clear_directory(dir):
    files = os.listdir(dir)
    for file_name in files:
        if file_name.endswith(".json"):
            print("File: " + file_name)
            clear_file(dir + file_name)


print("Clear JSON")
print("Processing module: Cuba...")
clear_directory("./cuba/cuba/custom/")
