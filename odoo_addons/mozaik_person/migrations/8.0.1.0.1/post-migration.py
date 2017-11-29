# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager

__name__ = "Recompute DISPLAY NAME of RES PARTNER"


def migrate(cr, version):
    if not version:
        return

    registry = RegistryManager.get(cr.dbname)
    partner_obj = registry['res.partner']
    k = 'display_name'
    f = partner_obj._columns['display_name']
    partner_obj._update_store(cr, f, k)
