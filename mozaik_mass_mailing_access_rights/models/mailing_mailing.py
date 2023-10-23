# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MassMailing(models.Model):

    _inherit = "mailing.mailing"

    sending_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Sending user",
        default=lambda self: self.env.user,
        copy=False,
    )

    def action_put_in_queue(self):
        self.write({"sending_user_id": self.env.user.id})
        super().action_put_in_queue()

    def _get_recipients(self):
        if self.sending_user_id:
            return super(
                MassMailing, self.with_user(self.sending_user_id.id)
            )._get_recipients()
        else:
            return super()._get_recipients()
