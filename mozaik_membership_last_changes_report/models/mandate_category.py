# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MandateCategory(models.Model):

    _inherit = "mandate.category"

    summary_mails_recipient = fields.Boolean()
