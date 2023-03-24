# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = ["product.template"]

    advance_workflow_as_paid = fields.Boolean(
        "Automatically create the following membership line",
        help="Tick for free subscriptions, e.g. sponsored ones. The workflow "
        "will advance as it does for paid subscriptions when partner pays",
    )
