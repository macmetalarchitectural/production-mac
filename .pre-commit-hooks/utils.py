#!/usr/bin/env python3
"""
Common utility functions for pre-commit hooks and GitHub actions.
"""
from pathlib import Path


def is_e3k_module(file_path):
    """
    Check if a file belongs to an e3k module.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if the file belongs to an e3k module, False otherwise
    """
    parts = Path(file_path).parts
    return any(part.startswith("e3k_") for part in parts)


def get_module_name(file_path):
    """
    Extract the Odoo module name from the file path.

    Args:
        file_path: Path to the file

    Returns:
        str or None: The module name or None if not found
    """
    parts = Path(file_path).parts
    for part in parts:
        if part.startswith("e3k_") or "__manifest__.py" in str(file_path):
            # Find the parent directory of the manifest
            path = Path(file_path)
            while path.parent != path:
                if (path / "__manifest__.py").exists():
                    return path.name
                path = path.parent
    return None


def is_odoo_module_path(path):
    """
    Check if a path corresponds to a valid Odoo module.

    Args:
        path: Path to check

    Returns:
        bool: True if it's a valid Odoo module
    """
    path = Path(path)
    if path.is_file():
        path = path.parent
    return (path / "__manifest__.py").exists() or (path / "__openerp__.py").exists()
