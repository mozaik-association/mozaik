# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    sta_candidature_ids = fields.One2many(
        comodel_name="sta.candidature",
        inverse_name="partner_id",
        string="State Candidatures",
        domain=[("active", "=", True)],
    )
    sta_candidature_inactive_ids = fields.One2many(
        comodel_name="sta.candidature",
        inverse_name="partner_id",
        string="State Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )
    int_candidature_ids = fields.One2many(
        comodel_name="int.candidature",
        inverse_name="partner_id",
        string="Internal Candidatures",
        domain=[("active", "=", True)],
    )
    int_candidature_inactive_ids = fields.One2many(
        comodel_name="int.candidature",
        inverse_name="partner_id",
        string="Internal Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )
    ext_candidature_ids = fields.One2many(
        comodel_name="ext.candidature",
        inverse_name="partner_id",
        string="External Candidatures",
        domain=[("active", "=", True)],
    )
    ext_candidature_inactive_ids = fields.One2many(
        comodel_name="ext.candidature",
        inverse_name="partner_id",
        string="External Candidatures (Inactive)",
        domain=[("active", "=", False)],
    )
