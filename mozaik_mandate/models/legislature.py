# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class Legislature(models.Model):

    _inherit = "legislature"

    def write(self, vals):
        new_deadline_date = vals.get("deadline_date", False)
        if new_deadline_date:
            new_deadline_date = datetime.strptime(
                new_deadline_date, DEFAULT_SERVER_DATE_FORMAT
            ).date()
            for legis in self:
                if legis.deadline_date != new_deadline_date:
                    if new_deadline_date < legis.deadline_date:
                        raise ValidationError(
                            _(
                                "New deadline date must be greater or"
                                " equal than the previous deadline date !"
                            )
                        )
                    mandate_obj = self.env["sta.mandate"]
                    mandates = mandate_obj.search(
                        [
                            ("legislature_id", "=", legis.id),
                            ("deadline_date", ">", new_deadline_date),
                        ]
                    )
                    if mandates:
                        mandates.write({"deadline_date": new_deadline_date})
        return super().write(vals)
