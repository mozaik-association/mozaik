# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class QueueJob(models.Model):

    _inherit = 'queue.job'

    @api.multi
    def _get_subscribe_users_domain(self):
        domain = super(QueueJob, self)._get_subscribe_users_domain()
        group = self.env.ref('connector_support.group_connector_support')
        if group:
            domain = [dom for dom in domain if dom[0] != 'groups_id']
            domain = [('groups_id', '=', group.id)] + domain
        return domain
