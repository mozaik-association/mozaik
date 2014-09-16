# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _inactive_cascade = True
    _allowed_inactive_link_models = ['res.partner']

    # ready for workflow !
    _enable_wkf = True

    def _update_follower(
            self, cr, uid, partner_ids, context=None):
        '''
        Update follower for each partner_ids
        '''
        res_vals = {}
        e_obj = self.pool['email.coordinate']
        pc_obj = self.pool['postal.coordinate']
        phc_obj = self.pool['phone.coordinate']
        p_obj = self.pool['res.partner']
        ia_obj = self.pool['int.assembly']
        for partner_id in partner_ids:
            int_instance_id = self.read(
                cr, uid, partner_id, ['int_instance_id'],
                context=context)['int_instance_id'][0]
            f_partner_ids = ia_obj.get_followers_assemblies(
                cr, uid, int_instance_id, context=context)
            # update even if f_partner_ids is void case to reset
            write_vals = {
                'message_follower_ids': [(6, 0, f_partner_ids)],
            }
            res_vals[partner_id] = write_vals
            p_obj.write(
                cr, uid, partner_id, write_vals, context=context)

            # partner are at least follower of their own coordinate
            f_partner_ids.append(partner_id)
            e_ids = e_obj.search(
                cr, uid, [('partner_id', '=', partner_id),
                          ('is_main', '=', True)], context=context)
            if e_ids:
                e_obj.write(cr, uid, e_ids, write_vals, context=context)

            pc_ids = pc_obj.search(
                cr, uid, [('partner_id', '=', partner_id),
                          ('is_main', '=', True)], context=context)
            if pc_ids:
                pc_obj.write(cr, uid, pc_ids, write_vals, context=context)

            phone_ids = phc_obj.search(
                cr, uid, [('partner_id', '=', partner_id),
                          ('is_main', '=', True)], context=context)
            if phone_ids:
                phc_obj.write(cr, uid, phone_ids, write_vals, context=context)

        return res_vals

    def _generate_membership_reference(self, cr, uid, partner_id,
                                       context=None):
        """
        This method will generate a membership reference for payment.
        Comm. Struct. = '9' + year without century +
            member identifier on 7 positions + % 97
        """
        partner = self.browse(cr, uid, partner_id, context=context)
        base_identifier = '0000000'
        identifier = '%s' % partner.identifier
        base = '9%s%s' % (('%s' % date.today().year)[2:],
                          ''.join((base_identifier[:-len(identifier)],
                                   identifier)))
        comm_struct = '%s%s' % (base, int(base) % 97 or 97)
        return '+++%s/%s/%s+++' % (comm_struct[:3], comm_struct[3:7],
                                   comm_struct[7:])

    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', 'Internal Instance', select=True,
            track_visibility='onchange'),
        'int_instance_m2m_ids': fields.many2many(
            'int.instance', 'res_partner_int_instance_rel', id1='partner_id',
            id2='int_instance_id', string='Internal Instances'),

        'subscription_product_id': fields.many2one(
            'product.product', string="Membership Type", select=True,
            domain="[('membership', '!=', False), ('list_price', '>', 0.0)]",
            track_visibility='onchange'),
        # membership fields: track visibility is done into membership history
        # management
        'membership_state_id': fields.many2one('membership.state',
                                               string='State'),
        'membership_state_code': fields.related('membership_state_id', 'code',
                                                string='Membership State Code',
                                                type="char", readonly=True),
        'accepted_date': fields.date('Accepted Date'),
        'decline_payment_date': fields.date('Decline Payment Date'),
        'rejected_date': fields.date('Rejected Date'),
        'resignation_date': fields.date('Resignation Date'),
        'exclusion_date': fields.date('Exclusion Date'),

        'del_doc_date': fields.date('Delivery Document Date'),
        'del_mem_card_date': fields.date('Delivery Member Card Date'),
        'reference': fields.char('Reference'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
        'subscription_product_id': lambda self, cr, uid, ids, context = None:
            self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'ficep_base', 'membership_product_free')[1],
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy m2m fields.
        """
        default = default or {}
        default.update({
            'int_instance_m2m_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default,
                                                 context=context)
        return res

    def create_workflow(self, cr, uid, ids, context=None):
        '''
        Create workflow only for natural persons
        '''
        dom = [('id', 'in', ids), ('is_company', '=', False)]
        pids = self.search(cr, uid, dom, context=context)
        res = super(res_partner, self).create_workflow(
            cr, uid, pids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        If partner has an identifier then update its followers
        '''
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        if vals.get('identifier', False):
            self._update_follower(cr, SUPERUSER_ID, [res], context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        Create or Delete workflow if necessary (according to the new
        is_company value)
        Invalidate some caches when changing set of instances related to
        the user
        """
        ids = isinstance(ids, (long, int)) and [ids] or ids
        if 'is_company' in vals:
            is_company = vals['is_company']
            data = self.read(cr, uid, ids, ['is_company'], context=context)
            p2d_ids = [
                # wkfs to delete
                d['id'] for d in data if not d['is_company'] and is_company
            ]
            if p2d_ids:
                ml_obj = self.pool['membership.membership_line']
                ml_ids = ml_obj.search(
                    cr, uid, [('partner', 'in', p2d_ids)],
                    context=context)
                if ml_ids:
                    raise orm.except_orm(
                        _('Error'),
                        _('A natural person with membership history '
                          'cannot be transformed to a legal person')
                    )
            p2c_ids = [
                # wkfs to create
                d['id'] for d in data if d['is_company'] and not is_company
            ]
            super(res_partner, self).create_workflow(
                cr, uid, p2c_ids, context=context)
            self.delete_workflow(
                cr, uid, p2d_ids, context=context)

            if is_company:
                vals['membership_state_id'] = None
        res = super(res_partner, self).write(
            cr, uid, ids, vals, context=context)

        if 'int_instance_m2m_ids' in vals:
            rule_obj = self.pool['ir.rule']
            for partner in self.browse(cr, uid, ids, context=context):
                for u in partner.user_ids:
                    rule_obj.clear_cache(cr, u.id)
            int_obj = self.pool['int.instance']
            int_obj.get_default.clear_cache(self)
        return res

# view methods: onchange, button

    def decline_payment(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'decline_payment_date':
                                         date.today().strftime('%Y-%m-%d')},
                          context=context)

    def reject(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'rejected_date': date.today().
                                         strftime('%Y-%m-%d')},
                          context=context)

    def exclude(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'exclusion_date': date.today().
                                         strftime('%Y-%m-%d')},
                          context=context)

    def resign(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'resignation_date': date.today().
                                         strftime('%Y-%m-%d')},
                          context=context)

    def button_modification_request(self, cr, uid, ids, context=None):
        """
        Create a `membership.request` object with the datas of the current
        partner. Launch it into the another form view
        """
        partners = self.browse(cr, uid, ids, context=context)
        partner = partners and partners[0]
        if not partner:
            raise orm.except_orm(_('Error'),
                                 _('Modification request must be ' +
                                   'launch with a valid partner id'))
        postal_coordinate_id = partner.postal_coordinate_id or False
        mobile_coordinate_id = partner.mobile_coordinate_id or False
        fix_coordinate_id = partner.fix_coordinate_id or False
        email_coordinate_id = partner.email_coordinate_id or False
        int_instance_id = partner.int_instance_id or False
        birth_date = partner.birth_date
        day = False
        month = False
        year = False
        if partner.birth_date:
            datas = partner.birth_date.split('-')
            day = datas[2]
            month = datas[1]
            year = datas[0]

        values = {
            'membership_state_id': partner.membership_state_id and
            partner.membership_state_id.id or False,
            'identifier': partner.identifier,
            'lastname': partner.lastname,
            'firstname': partner.firstname,
            'gender': partner.gender,
            'birth_date': birth_date,
            'day': day,
            'month': month,
            'year': year,
            'is_update': True,

            # country_id is mandatory
            'country_id': postal_coordinate_id and postal_coordinate_id.
            address_id.country_id.id,
            'address_local_street_id': postal_coordinate_id and
            postal_coordinate_id.address_id.address_local_street_id.id,
            'street_man': postal_coordinate_id and postal_coordinate_id.
            address_id.street_man,
            'street2': postal_coordinate_id and postal_coordinate_id.
            address_id.street2,
            'address_local_zip_id': postal_coordinate_id and
            postal_coordinate_id.address_id.address_local_zip_id.id,
            'zip_man': postal_coordinate_id and
            postal_coordinate_id.address_id.zip_man,
            'town_man': postal_coordinate_id and
            postal_coordinate_id.address_id.town_man,
            'box': postal_coordinate_id and
            postal_coordinate_id.address_id.box,
            'number': postal_coordinate_id and
            postal_coordinate_id.address_id.number,

            'mobile': mobile_coordinate_id and
            mobile_coordinate_id.phone_id.name,
            'phone': fix_coordinate_id and fix_coordinate_id.phone_id.name,
            'mobile_id': mobile_coordinate_id and
            mobile_coordinate_id.phone_id.id,
            'phone_id': fix_coordinate_id and fix_coordinate_id.phone_id.id,

            'email': email_coordinate_id and email_coordinate_id.email,

            'partner_id': partner.id,
            'address_id': postal_coordinate_id and postal_coordinate_id.
            address_id.id,
            'int_instance_id': int_instance_id and int_instance_id.id,

            'interests_m2m_ids': [[6, False, partner.interests_m2m_ids and
                                   [interest.id for interest in partner.
                                    interests_m2m_ids] or []]],
            'competencies_m2m_ids': [[6, False, partner.competencies_m2m_ids
                                      and [competence.id for competence in
                                           partner.competencies_m2m_ids] or
                                      []]],
        }
        membership_request_obj = self.pool['membership.request']
        context['mode'] = 'ws'
        membership_request_id = membership_request_obj.create(cr, uid, values,
                                                              context=context)
        return membership_request_obj.display_object_in_form_view(
            cr, uid, membership_request_id, context=context)

# workflow

    def update_state(self, cr, uid, ids, membership_state_code, context=None):
        """
        Partner membership_state_id is updated with the `membership.state`\
        having the `code` `membership_state_code`

        :type membership_state_code: char
        :param membership_state_code: code of `membership.state`
        :raise orm.except_orm: If no membership_state_id found with \
        `membership_state_code`
        """

        membership_state_obj = self.pool['membership.state']
        membership_state_ids = membership_state_obj.search(
            cr, uid, [('code', '=', membership_state_code)], context=context)

        if not membership_state_ids:
            raise orm.except_orm(
                _('Error'),
                _('Try to set an undefined "Membership State" on partner'))

        vals = {
            'membership_state_id': membership_state_ids[0],
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
            'reference': membership_state_code in [
                'member_candidate',
                'member',
            ] and self._generate_membership_reference(
                cr, uid, ids, context=context) or False
        }

        res = self.write(cr, uid, ids, vals, context=context)
        state_id = membership_state_obj._state_default_get(
            cr, uid, context=context)
        default_code = membership_state_obj.read(
            cr, uid, state_id, ['code'], context=context)['code']

        if membership_state_code != default_code:
            self.update_membership_line(cr, uid, ids, context=context)

        return res

    def update_membership_line(self, cr, uid, ids, context=None):
        """
        Search for a `membership.membership_line` for each partner
        If no membership_line exist:
        * then create one
        * else invalidate it updating its `date_to` and duplicate it
          with the right state
        """
        today = date.today().strftime('%Y-%m-%d')
        values = {
            'date_from': today,
            'date_to': False,
        }
        membership_line_obj = self.pool['membership.membership_line']
        membership_state_obj = self.pool['membership.state']
        for partner in self.browse(cr, uid, ids, context=context):
            values['membership_state_id'] = partner.membership_state_id.id
            if values['membership_state_id'] != \
                    membership_state_obj._state_default_get(cr, uid):
                values['int_instance_id'] = partner.int_instance_id and \
                    partner.int_instance_id.id or False,
                values['reference'] = partner.reference
                current_membership_line_ids = membership_line_obj.search(
                    cr, uid, [('partner', '=', partner.id),
                              ('active', '=', True)],
                    context=context)
                current_membership_line_id = current_membership_line_ids and \
                    current_membership_line_ids[0] or False

                if current_membership_line_id:
                    # update and copy it
                    vals = {
                        'date_to': today,
                    }
                    membership_line_obj.action_invalidate(
                        cr, uid, [current_membership_line_id],
                        context=context, vals=vals)
                    membership_line_obj.copy(
                        cr, uid, current_membership_line_id, default=values,
                        context=context)
                else:
                    # create first membership_line
                    values.update({
                        'partner': partner.id,
                        'date': today,
                        'membership_id': partner.subscription_product_id and
                        partner.subscription_product_id.id or False,
                        'member_price': partner.subscription_product_id and
                        partner.subscription_product_id.list_price or 0.0,
                    })
                    membership_line_obj.create(
                        cr, uid, values, context=context)
