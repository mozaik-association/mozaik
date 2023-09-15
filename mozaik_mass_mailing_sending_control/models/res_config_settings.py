# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    mass_mailing_sending_control = fields.Boolean(
        string="Add control option for big sendings",
        config_parameter="mass_mailing.sending_control",
        help="Enable a second control for big mass mailing sendings",
    )

    mass_mailing_sending_control_number = fields.Integer(
        string="Minimum number of recipients for sending control",
        config_parameter="mass_mailing.sending_control_number",
        help="For mass mailings having more than this number of recipients, "
        "enable a control before sending.",
    )
