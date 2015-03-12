# -*- encoding: utf-8 -*-

__name__ = "Remove useless IDENTIFIER column in table MEMBERSHIP_REQUEST"


def migrate(cr, version):
    if not version:
        return
    cr.execute('SELECT 1 '
               'FROM pg_class c,pg_attribute a '
               'WHERE c.relname=%s '
               'AND c.oid=a.attrelid '
               'AND a.attname = %s', ('membership_request', 'identifier'))
    if cr.fetchone():
        cr.execute("ALTER TABLE membership_request "
                   "DROP COLUMN identifier")
