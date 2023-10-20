# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models, tools


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    def copy(self, default=None):
        """
        * When duplicating a mass mailing, the responsible will be
          the user duplicating it.
        * Odoo override copy on mass mailings to force adding a _("(copy)")
          in the name. We want to remove this string and set the name
          as when creating a new mass mailing.
        """
        default = dict(default or {}, user_id=self.env.user.id)
        res = super().copy(default)
        # The copy method is decorated in mass_mailing module with @api.returns
        # to return only the res.id. It implies that modifications made to
        # res are not taken into account. We must browse the created
        # record to modify the name.
        rec_in_memory = self.browse(res.id)
        rec_in_memory.name = "%s %s" % (
            res.subject,
            datetime.strftime(
                fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT
            ),
        )
        return res
