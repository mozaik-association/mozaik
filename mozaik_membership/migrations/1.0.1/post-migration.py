# -*- encoding: utf-8 -*-

__name__ = "Remove useless IDENTIFIER column in table MEMBERSHIP_REQUEST"


def migrate(cr, version):
    if not version:
        return
    cr.execute("ALTER TABLE membership_request "
               "DROP COLUMN identifier")
