# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = 'partner.involvement.category'

    automatic_supporter = fields.Boolean(
        default=False, track_visibility='onchange')
