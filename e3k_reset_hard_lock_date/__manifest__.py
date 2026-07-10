# -*- coding: utf-8 -*-
{
    "name": "Réinitialiser le verrou définitif (correctif ponctuel)",
    "summary": "Efface le Verrou définitif (hard lock date) posé par erreur",
    "description": """
One-shot fix module.

The 'Hard Lock Date' (res.company.hard_lock_date) is irreversible through the
ORM: res.company.write() calls _validate_locks(), which raises a UserError as
soon as the date is removed or moved backward. There is therefore no UI, shell
or XML-RPC way to clear it.

This module clears it with a raw SQL statement (bypassing the Python guard) in
its post_init_hook, i.e. once, at install time. It only touches
hard_lock_date; the soft lock dates (sales/purchases/tax/global) stay untouched
and can still be edited normally from the UI.

Install once on production, confirm the field is empty, then uninstall/remove.
""",
    "category": "Accounting",
    "version": "19.0.1.0.0",
    "author": "e3k",
    "website": "https://e3k.co",
    "depends": ["account"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
}