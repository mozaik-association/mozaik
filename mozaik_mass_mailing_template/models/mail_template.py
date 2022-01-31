# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailTemplate(models.Model):

    _inherit = "mail.template"

    use_default_to = fields.Boolean(default=True)
