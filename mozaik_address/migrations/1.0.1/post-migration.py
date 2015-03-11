# -*- encoding: utf-8 -*-

__name__ = 'Remove useless "N/A: " for column address of RES_PARTNER'


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE res_partner "
        "SET address = substring(address, 6) "
        "WHERE address like 'N/A: %'"
    )
