# -*- encoding: utf-8 -*-

__name__ = "Re-Active workflow.instance for dead-end membership' state"


def migrate(cr, version):
    if not version:
        return
    SQL_QUERY = '''
    UPDATE
        wkf_instance
    SET
        state = 'active'
    WHERE
        res_type = 'res.partner'
        AND
        state = 'complete'
    '''
    cr.execute(SQL_QUERY)