# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')
    amount = fields.Float(
        digits=dp.get_precision('Product Price'), readonly=True)

    @api.multi
    def button_modification_request(self):
        """
        Create a `membership.request` from a partner
        """
        self.ensure_one()
        membership_request = self.env['membership.request']
        mr = membership_request.search(
            [('partner_id', '=', self.id), ('state', '=', 'draft')])
        if not mr:
            postal_coordinate_id = self.postal_coordinate_id
            address_id = postal_coordinate_id.address_id
            birth_date = self.birth_date
            day = False
            month = False
            year = False
            if birth_date:
                dt = birth_date.split('-')
                day = dt[2]
                month = dt[1]
                year = dt[0]

            state_id = self.membership_state_id.id or False
            categories = self.partner_involvement_ids.mapped(
                'involvement_category_id').filtered(lambda s: s.code)
            competencies = self.competencies_m2m_ids
            values = {
                'membership_state_id': state_id,
                'result_type_id': state_id,
                'identifier': self.identifier,
                'lastname': self.lastname,
                'firstname': self.firstname,
                'gender': self.gender,
                'birth_date': birth_date,
                'day': day,
                'month': month,
                'year': year,
                'is_update': True,
                'country_id': address_id.country_id.id or False,
                'address_local_street_id': (
                    address_id.address_local_street_id.id or False),
                'street_man': address_id.street_man or False,
                'street2': address_id.street2 or False,
                'address_local_zip_id': (
                    address_id.address_local_zip_id.id or False),
                'zip_man': address_id.zip_man or False,
                'town_man': address_id.town_man or False,
                'box': address_id.box or False,
                'number': address_id.number or False,
                'mobile': self.mobile_coordinate_id.phone_id.name or False,
                'phone': self.fix_coordinate_id.phone_id.name or False,
                'mobile_id': self.mobile_coordinate_id.phone_id.id or False,
                'phone_id': self.fix_coordinate_id.phone_id.id or False,
                'email': self.email_coordinate_id.email or False,
                'partner_id': self.id,
                'address_id': address_id.id or False,
                'int_instance_id': self.int_instance_id.id or False,
                'interests_m2m_ids': [(6, 0, self.interests_m2m_ids.ids)],
                'competencies_m2m_ids': [(6, 0, competencies.ids)],
                'involvement_category_ids': [(6, 0, categories.ids)],
                'local_voluntary': self.local_voluntary,
                'regional_voluntary': self.regional_voluntary,
                'national_voluntary': self.national_voluntary,
            }
            # create mr in sudo mode for portal user allowing to avoid create
            # rights on this model for these users
            if 'default_open_partner_user' in self.env.context:
                membership_request = membership_request.sudo()
            mr = membership_request.create(values)
        res = mr.display_object_in_form_view()[0]
        return res
