# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    nationality_id = fields.Many2one(track_visibility='onchange')
