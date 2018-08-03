# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResUsers(models.AbstractModel):
    _inherit = 'res.users'

    @api.multi
    def _create_welcome_message(self):
        """
        Do not call the super to avoid creation of mail.message
        :return: mail.message recordset
        """
        return self.env["mail.message"].browse()
