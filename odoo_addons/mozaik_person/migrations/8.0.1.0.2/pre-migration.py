# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from openerp import api, SUPERUSER_ID

__name__ = "Drop obsolete index"


def migrate(cr, version):
    if not version:
        return

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        q = "DROP INDEX partner_involvement_unique_idx"
        env.cr.execute(q)

        q = "DROP INDEX " \
            "partner_involvement_partner_involvement_category_id_index"
        env.cr.execute(q)
