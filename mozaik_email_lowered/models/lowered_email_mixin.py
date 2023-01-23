# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.mozaik_tools.tools import format_email


class MozaikLoweredEmailMixin(models.AbstractModel):

    _name = "mozaik.lowered.email.mixin"
    _description = "Mozaik Lowered Email Mixin"

    email = fields.Char()
    lowered_email = fields.Char(compute="_compute_lowered_email", store=True)

    @api.depends("email")
    def _compute_lowered_email(self):
        for rec in self:
            rec.lowered_email = format_email(rec.email) if rec.email else False

    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        When searching with '=ilike' on emails, search with '=' on
        lowered_email
        """
        new_args = []
        for arg in args:
            if (
                isinstance(arg, (list, tuple))
                and arg[0] == "email"
                and arg[1] == "=ilike"
                and isinstance(arg[2], str)
            ):
                search_field_name = "lowered_email"
                operator = "="
                value = format_email(arg[2])
                new_args.append((search_field_name, operator, value))
            else:
                new_args.append(arg)
        return super().search(new_args, offset, limit, order, count)
