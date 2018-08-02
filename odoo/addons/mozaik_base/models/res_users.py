# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    _order = 'partner_id'

    groups_id = fields.Many2many(
        default=False,
    )

    @api.multi
    def name_get(self):
        """
        Edit the name get of res.users
        Should be: name (login)
        :return: list of tuple (int, str)
        """
        results = super(ResUsers, self).name_get()
        users = self.browse([r[0] for r in results])
        new_result = [(u.id, "%s (%s)" % (u.name, u.login)) for u in users]
        return new_result
