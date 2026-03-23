#!/usr/bin/env python3
import sys
import ast
from pathlib import Path
from utils import is_e3k_module

def check_author(manifest_path):
    """
    Verify that the author in the manifest is 'e3k'.

    Args:
        manifest_path: Path to the __manifest__.py file

    Returns:
        bool: True if the author is valid, False otherwise
    """
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        data = ast.literal_eval(content)
        author = data.get("author", "")
        if author != "e3k":
            print(f"[ERROR] Invalid author in {manifest_path}: '{author}' (expected 'e3k')")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Failed to read {manifest_path}: {e}")
        return False

def main():
    """
    Main entry point of the script.
    Verifies the author only for e3k modules.
    """
    success = True
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.name == "__manifest__.py":
            # Verify only e3k modules
            if is_e3k_module(path):
                if not check_author(path):
                    success = False
            else:
                print(f"[INFO] Skipping non-e3k module: {path.parent.name}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
