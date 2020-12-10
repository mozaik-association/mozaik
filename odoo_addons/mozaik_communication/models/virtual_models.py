# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

from openerp.addons.mozaik_person.models.partner_involvement \
    import CATEGORY_TYPE

class VirtualPartnerInvolvement(models.Model):

    _inherit = ["virtual.partner.involvement","virtual.partner.thesaurus.child.search"]
    _name = "virtual.partner.involvement"

    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()

    nationality_id = fields.Many2one(
        comodel_name='res.country', string='Nationality')
    involvement_type = fields.Selection(selection=CATEGORY_TYPE)
    effective_time = fields.Datetime(string='Involvement Date')
    promise = fields.Boolean()


class VirtualPartnerInstance(models.Model):

    _inherit = "virtual.partner.instance"

    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()
    nationality_id = fields.Many2one(
        comodel_name='res.country', string='Nationality')