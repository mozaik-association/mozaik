# -*- coding: utf-8 -*-
from openerp.tools import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

__name__ = "Delete from Table thesaurus_term"


def migrate(cr, version):
    if not version:
        return

    registry = RegistryManager.get(cr.dbname)
    thesaurus_term_obj = registry['thesaurus.term']
    thesaurus_term_ids = thesaurus_term_obj.search(cr, SUPERUSER_ID, [])
    thesaurus_term_obj.unlink(cr, SUPERUSER_ID, thesaurus_term_ids)
