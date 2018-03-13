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
    local_only = fields.Boolean(
        track_visibility='onchange',
        help='Partner wishing to be contacted only by the local')
    amount = fields.Float(
        digits=dp.get_precision('Product Price'), readonly=True)

    @api.multi
    def update_state(self, membership_state_code):
        """
        Update state of partner. Called by workflow.

        :type membership_state_code: char
        :param membership_state_code: code of `membership.state`
        """
        self.ensure_one()
        membership_state_obj = self.env['membership.state']
        state = membership_state_obj.search(
            [('code', '=', membership_state_code)], limit=1)

        vals = {
            'membership_state_id': state.id,
            'accepted_date': False,
            'decline_payment_date': False,
            'rejected_date': False,
            'resignation_date': False,
            'exclusion_date': False,
            'customer': membership_state_code in [
                'member_candidate',
                'member_committee',
                'member',
                'former_member',
                'former_member_committee',
            ],
            'reference': False,
            'amount': False,
        }

        if membership_state_code == 'supporter':
            vals['free_member'] = True

        if membership_state_code == 'member_candidate':
            vals['del_doc_date'] = False

        # force voluntaries fields if any
        if membership_state_code in [
                'without_membership', 'supporter', 'former_supporter']:
            vals.update({
                'local_voluntary': False,
                'regional_voluntary': False,
                'national_voluntary': False,
            })
        elif any([
            membership_state_code == 'member_candidate' and
            self.membership_state_code in [
                'without_membership', 'supporter'],
            membership_state_code == 'member_committee' and
                self.membership_state_code == 'supporter']):
            vals.update({
                'local_voluntary': True,
                'regional_voluntary': True,
                'national_voluntary': True,
            })

        # force local only field if any
        if membership_state_code in [
                'supporter', 'former_supporter', 'member_candidate',
                'member_committee', 'member', 'former_member',
                'former_member_committee']:
            vals['local_only'] = False

        current_reference = self.reference
        date_from = self.accepted_date

        res = self.write(vals)

        if membership_state_code != 'without_membership':
            self._update_membership_line(
                ref=current_reference, date_from=date_from)

        return res

    @api.multi
    def _update_membership_line(self, ref=False, date_from=False):
        """
        Search for a `membership.membership_line` for each partner
        If no membership_line exist:
        * then create one
        * else invalidate it updating its `date_to` and duplicate it
          with the right state
        """
        date_from = date_from or fields.Date.today()
        values = {
            'date_from': date_from,
            'date_to': False,
        }
        membership_line_obj = self.env['membership.line']
        membership_state_obj = self.env['membership.state']
        def_state_id = membership_state_obj._state_default_get()
        for partner in self.filtered(lambda s: not s.is_company):
            values['partner_id'] = partner.id
            values['state_id'] = partner.membership_state_id.id
            if values['state_id'] != def_state_id:
                values['int_instance_id'] = partner.int_instance_id and \
                    partner.int_instance_id.id or False,
                values['reference'] = ref
                current_membership_line_id = membership_line_obj.search(
                    [('partner_id', '=', partner.id), ('active', '=', True)],
                    limit=1)

                if current_membership_line_id:
                    # update and copy it
                    current_membership_line_id.action_invalidate(
                        vals={'date_to': date_from})
                    current_membership_line_id.copy(default=values)
                else:
                    # create first membership_line
                    membership_line_obj.create(values)

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
                'local_voluntary': self.local_voluntary,
                'regional_voluntary': self.regional_voluntary,
                'national_voluntary': self.national_voluntary,
                'local_only': self.local_only,
                'nationality_id': self.nationality_id.id or False,
            }
            # create mr in sudo mode for portal user allowing to avoid create
            # rights on this model for these users
            if 'default_open_partner_user' in self.env.context:
                membership_request = membership_request.sudo()
            mr = membership_request.create(values)
        res = mr.display_object_in_form_view()[0]
        return res
