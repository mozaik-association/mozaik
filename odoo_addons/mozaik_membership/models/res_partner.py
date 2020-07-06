# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    current_membership_line_id = fields.Many2one(
        comodel_name='membership.line', string='Current Membership',
        compute='_compute_current_membership_line_id')

    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')
    local_only = fields.Boolean(
        track_visibility='onchange',
        help='Partner wishing to be contacted only by the local')
    amount = fields.Float(
        digits=dp.get_precision('Product Price'), readonly=True)

    @api.multi
    @api.depends('membership_line_ids', 'membership_line_ids.active')
    def _compute_current_membership_line_id(self):
        for partner in self:
            current_membership_line_id = partner.membership_line_ids.filtered(
                lambda s: s.active) or False
            partner.current_membership_line_id = current_membership_line_id

    @api.multi
    def update_state(self, membership_state_code):
        """
        Update state of partner. Called by workflow.

        :type membership_state_code: char
        :param membership_state_code: code of `membership.state`
        """
        self.ensure_one()
        if not self.env.context.get('lang'):
            self = self.with_context(lang=self.lang)
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

        res = self.write(vals)

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
                'indexation_comments': self.indexation_comments,
            }
            # create mr in sudo mode for portal user allowing to avoid create
            # rights on this model for these users
            if 'default_open_partner_user' in self.env.context:
                membership_request = membership_request.sudo()
            mr = membership_request.create(values)
        res = mr.display_object_in_form_view()[0]
        return res

    @api.multi
    def create_workflow(self):
        '''
        Create workflow only for natural persons
        '''
        naturals = self.filtered(lambda s: not s.is_company)
        res = super(ResPartner, naturals).create_workflow()
        return res

    @api.multi
    def write(self, vals):
        """
        Create or Delete workflow if necessary (according to the new
        is_company value)
        Update followers when changing internal instance
        Add membership line when changing internal instance or state
        Invalidate some caches when changing set of instances related to
        the user
        """
        if 'is_company' in vals:
            is_company = vals['is_company']
            p2d = self.filtered(lambda s, c=is_company: not s.is_company and c)
            if p2d.mapped('membership_line_ids'):
                raise ValidationError(
                    _('A natural person with membership history '
                      'cannot be transformed to a legal person')
                )
            p2c = self.filtered(lambda s, c=is_company: s.is_company and not c)
            super(ResPartner, p2c).create_workflow()
            p2d.delete_workflow()

            if is_company:
                # reset state for a company
                vals['membership_state_id'] = None

        p_upd_fol = self.env['res.partner']
        p_add_line = self.env['res.partner']
        if vals.get('int_instance_id'):
            int_instance_id = vals['int_instance_id']
            p_upd_fol = self.filtered(
                lambda s, ii=int_instance_id: s.int_instance_id.id != ii)
            p_add_line |= p_upd_fol
            # subscribe related assemblies before updating partner
            # followers list will be entirely reinitialize later
            p_upd_fol._subscribe_assemblies(int_instance_id=int_instance_id)

        previous_data = {}
        if vals.get('membership_state_id'):
            p_add_line |= self
            previous_data = self.read(['accepted_date', 'reference'])
            previous_data = {data['id']: data for data in previous_data}

        res = super(ResPartner, self).write(vals)

        # add a membership lines if any
        for partner in p_add_line:
            data = previous_data.get(partner.id, {})
            partner._update_membership_line(
                ref=data.get('reference'),
                date_from=data.get('accepted_date'))

        # update partners followers
        p_upd_fol.sudo()._update_followers()

        if 'int_instance_m2m_ids' in vals:
            rule_obj = self.env['ir.rule']
            rule_obj.clear_cache()

        return res
