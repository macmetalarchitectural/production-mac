# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Clear the irreversible Hard Lock Date that was set by mistake.

    The Hard Lock Date is intentionally irreversible through the ORM:
    ``res.company.write()`` -> ``_validate_locks()`` raises a ``UserError`` when
    the date is removed or moved backward. There is no database-level
    constraint, so a raw SQL write clears it cleanly. This does NOT alter any
    posted journal entry or its inalterable hash; it only re-allows editing
    before that date.

    Only ``hard_lock_date`` is touched. The soft lock dates
    (sale/purchase/tax/fiscalyear) are reversible from the UI and are left as-is.

    Scoped to company id=1 (M.A.C. Métal Architectural Inc.) so it can only ever
    affect that single company.
    """
    company_id = 1

    env.cr.execute(
        "SELECT id, name, hard_lock_date "
        "FROM res_company "
        "WHERE id = %s AND hard_lock_date IS NOT NULL",
        (company_id,),
    )
    rows = env.cr.fetchall()

    if not rows:
        _logger.info(
            "e3k_reset_hard_lock_date: company id=%s has no hard lock date set; nothing to do.",
            company_id,
        )
        return

    for cid, name, hard_lock_date in rows:
        _logger.warning(
            "e3k_reset_hard_lock_date: clearing hard_lock_date=%s on company id=%s (%s)",
            hard_lock_date, cid, name,
        )

    env.cr.execute(
        "UPDATE res_company SET hard_lock_date = NULL WHERE id = %s",
        (company_id,),
    )
    # Drop the cached (computed) values so the change is visible without a restart.
    env["res.company"].invalidate_model(["hard_lock_date", "user_hard_lock_date"])

    _logger.warning(
        "e3k_reset_hard_lock_date: cleared the hard lock date on %s company(ies).",
        len(rows),
    )