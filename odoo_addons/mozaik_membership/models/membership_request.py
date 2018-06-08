# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

import openerp.addons.decimal_precision as dp

from openerp.addons.mozaik_address.address_address import COUNTRY_CODE


class MembershipRequest(models.Model):

    _inherit = 'membership.request'

    @api.model
    def _get_status_values(self, request_type, date_from=False):
        """
        :type request_type: char
        :param request_type: m or s for member or supporter.
            `False` if not defined
        :rtype: dict
        :rparam: affected date resulting of the `request_type`
            and the `status`
        """
        vals = {}
        if request_type in ['m', 's']:
            vals['accepted_date'] = date_from or fields.Date.today()
            vals['free_member'] = (request_type == 's')
        return vals

    local_voluntary = fields.Boolean(track_visibility='onchange')
    regional_voluntary = fields.Boolean(track_visibility='onchange')
    national_voluntary = fields.Boolean(track_visibility='onchange')
    local_only = fields.Boolean(
        track_visibility='onchange',
        help='Partner wishing to be contacted only by the local')

    involvement_category_ids = fields.Many2many(
        'partner.involvement.category',
        relation='membership_request_involvement_category_rel',
        column1='request_id', column2='category_id',
        string='Involvement Categories')

    amount = fields.Float(
        digits=dp.get_precision('Product Price'), copy=False)
    reference = fields.Char(copy=False)
    effective_time = fields.Datetime(copy=False, string='Involvement Date')

    nationality_id = fields.Many2one(
        comodel_name='res.country', string='Nationality',
        track_visibility='onchange')

    @api.model
    def _pre_process(self, vals):
        """
        * Try:
        ** to find a zipcode and a country
        ** to build a birth_date
        ** to find an existing partner
        ** to find coordinates

        :rparam vals: updated input values dictionary ready
                      to create a ``membership_request``
        """
        mobile_id = False
        phone_id = False

        is_company = vals.get('is_company', False)
        firstname = False if is_company else vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        birth_date = False if is_company else vals.get('birth_date', False)
        day = False if is_company else vals.get('day', False)
        month = False if is_company else vals.get('month', False)
        year = False if is_company else vals.get('year', False)
        gender = False if is_company else vals.get('gender', False)
        email = vals.get('email', False)
        mobile = vals.get('mobile', False)
        phone = vals.get('phone', False)
        address_id = vals.get('address_id', False)
        address_local_street_id = vals.get('address_local_street_id', False)
        address_local_zip_id = vals.get('address_local_zip_id', False)
        number = vals.get('number', False)
        box = vals.get('box', False)
        town_man = vals.get('town_man', False)
        country_id = vals.get('country_id', False)
        zip_man = vals.get('zip_man', False)
        street_man = vals.get('street_man', False)

        partner_id = vals.get('partner_id', False)

        request_type = vals.get('request_type', False)

        zids = False
        if zip_man and town_man:
            domain = [
                ('local_zip', '=', zip_man),
                ('town', 'ilike', town_man),
            ]
            zids = self.env['address.local.zip'].search(domain, limit=1)
        if not zids and zip_man and not town_man and not country_id:
            domain = [
                ('local_zip', '=', zip_man),
            ]
            zids = self.env['address.local.zip'].search(domain, limit=1)
        if zids:
            cnty_id = self.env['res.country']._country_default_get(
                COUNTRY_CODE)
            if not country_id or cnty_id == country_id:
                country_id = cnty_id
                address_local_zip_id = zids.id
                town_man = False
                zip_man = False

        if not is_company and not birth_date:
            birth_date = self.get_birth_date(day, month, year)
        if mobile:
            mobile = self.get_format_phone_number(mobile)
            mobile_id = self.get_phone_id(mobile, 'mobile')
        if phone:
            phone = self.get_format_phone_number(phone)
            phone_id = self.get_phone_id(phone, 'fix')
        if email:
            email = self.get_format_email(email)

        if not partner_id:
            partner_id = self.get_partner_id(
                is_company, birth_date, lastname, firstname, email)

        technical_name = self.get_technical_name(
            address_local_street_id, address_local_zip_id, number,
            box, town_man, street_man, zip_man, country_id)
        address_id = address_id or self.onchange_technical_name(
            technical_name)['value']['address_id']
        int_instance_id = self.get_int_instance_id(address_local_zip_id)

        res = self.onchange_partner_id(
            is_company, request_type, partner_id, technical_name)['value']
        vals.update(res)

        vals.update({
            'is_company': is_company,
            'partner_id': partner_id,

            'lastname': lastname,
            'firstname': firstname,
            'birth_date': birth_date,

            'int_instance_id': res.get('int_instance_id') or int_instance_id,

            'day': day,
            'month': month,
            'year': year,
            'gender': gender,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'mobile_id': mobile_id,
            'phone_id': phone_id,

            'address_id': address_id,
            'address_local_zip_id': address_local_zip_id,
            'country_id': country_id,
            'zip_man': zip_man,
            'town_man': town_man,

            'technical_name': technical_name,
        })

        return vals

    @api.multi
    def validate_request(self):
        """
        * create additional involvements
        * for new member, if any, save also its reference and amount
        * for donation, if any, save also its reference and amount
        * update voluntaries and local only fields
        """
        self.ensure_one()
        former_code = False
        if self.partner_id:
            former_code = self.partner_id.membership_state_code
        res = super(MembershipRequest, self).validate_request()
        partner = self.partner_id
        new_code = partner.membership_state_code

        # create new involvements
        current_categories = self.partner_id.partner_involvement_ids.mapped(
            'involvement_category_id')
        new_categories = self.involvement_category_ids.filtered(
            lambda s, cc=current_categories:
            s not in cc or s.allow_multi)
        for ic in new_categories:
            vals = {
                'partner_id': self.partner_id.id,
                'effective_time': self.effective_time,
                'involvement_category_id': ic.id,
            }
            if ic.involvement_type == 'donation':
                vals.update({
                    'reference': self.reference,
                    'amount': self.amount,
                })
            self.env['partner.involvement'].create(vals)

        vals = {}
        # save membership amount
        if self.amount > 0.0 and self.reference:
            if (self.membership_state_id.code == 'without_membership' and
                    partner.membership_state_code == 'member_candidate'):
                vals.update({
                    'reference': self.reference,
                    'amount': self.amount,
                })

        # save voluntaries
        if new_code not in [
                False, 'without_membership',
                'supporter', 'former_supporter'] and not any([
                new_code == 'member_candidate' and
                former_code in [
                    False, 'without_membership', 'supporter'],
                new_code == 'member_committee' and
                    former_code == 'supporter']):
            vals.update({
                'local_voluntary': self.local_voluntary,
                'regional_voluntary': self.regional_voluntary,
                'national_voluntary': self.national_voluntary,
            })

        # save local only
        if new_code not in [
                'supporter', 'former_supporter', 'member_candidate',
                'member_committee', 'member', 'former_member',
                'former_member_committee']:
            vals['local_only'] = self.local_only

        # update the partner
        partner.write(vals)

        return res
