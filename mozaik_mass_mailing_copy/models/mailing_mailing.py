# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """
        When duplicating a mass mailing, the responsible will be
        the user duplicating it.
        """
        default = dict(default or {}, user_id=self.env.user.id)
        return super().copy(default)
