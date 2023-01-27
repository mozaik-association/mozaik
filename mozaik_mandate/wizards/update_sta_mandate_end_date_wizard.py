# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UpdateStaMandateEndDateWizard(models.TransientModel):

    _inherit = "abstract.update.mandate.end.date.wizard"
    _name = "update.sta.mandate.end.date.wizard"
    _description = "Update Sta Mandate End Date Wizard"

    mandate_ids = fields.Many2many(comodel_name="sta.mandate")
