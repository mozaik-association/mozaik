# -*- encoding: utf-8 -*-
from openerp import api, SUPERUSER_ID

__name__ = 'Transform distribution list m2o to a m2m'


def migrate(cr, version):
    if not version:
        # it is the installation of the module
        return

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        q = """
            INSERT INTO membership_request_distribution_list_rel
            (request_id, list_id)
            SELECT id, distribution_list_id
            FROM   membership_request
            WHERE  distribution_list_id IS NOT NULL
            """

        cr.execute(q)

        pass
