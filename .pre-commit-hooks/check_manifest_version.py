#!/usr/bin/env python
import re
import sys
import ast
from pathlib import Path
from utils import is_e3k_module

# Regex for x.y.z format (e.g.: 1.2.3)
VERSION_REGEX = r'^\d+\.\d+\.\d+$'

def validate_version_format(file_path):
    """
    Validate that the version in the manifest follows the x.y.z format.

    Args:
        file_path: Path to the __manifest__.py file

    Returns:
        bool: True if the version format is valid, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            manifest = ast.literal_eval(content)
            version = manifest.get("version", "")
            if not re.match(VERSION_REGEX, version):
                print(f"[ERROR] {file_path}: version '{version}' is not in format x.y.z")
                return False
            return True
    except Exception as e:
        print(f"[WARNING] {file_path}: Failed to parse manifest: {e}")
        return False

def main():
    """
    Main entry point of the script.
    Validates version format for e3k modules.
    """
    failed = False
    for file in sys.argv[1:]:
        path = Path(file)
        if path.name == "__manifest__.py":
            if not is_e3k_module(path):
                print(f"[INFO] Skipping non-e3k module: {path.parent.name}")
                continue

            if not validate_version_format(path):
                failed = True
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
