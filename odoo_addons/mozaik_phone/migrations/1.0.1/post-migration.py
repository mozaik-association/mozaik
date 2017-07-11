# -*- encoding: utf-8 -*-

__name__ = 'Remove useless "N/A: " for column phone, mobile, fax '\
           'of RES_PARTNER'


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE res_partner "
        "SET phone = substring(phone, 6) "
        "WHERE phone like 'N/A: %';"
        "UPDATE res_partner "
        "SET mobile = substring(mobile, 6) "
        "WHERE mobile like 'N/A: %'; "
        "UPDATE res_partner "
        "SET fax = substring(fax, 6) "
        "WHERE fax like 'N/A: %';"
    )
