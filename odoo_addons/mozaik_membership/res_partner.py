# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date

from openerp import api
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _


# Constants
AVAILABLE_PARTNER_KINDS = [
    ('a', 'Assembly'),
    ('t', 'Technical'),
    ('c', 'Company'),
    ('p', 'Partner'),
    ('m', 'Member'),
]

XML_IDS = {
    'email.coordinate': [
        'mozaik_membership.former_email_notification',
        'mozaik_membership.main_email_notification',
        'mozaik_email.email_failure_notification',
    ],
    'phone.coordinate': [
        'mozaik_membership.former_phone_id_notification',
        'mozaik_membership.main_phone_id_notification',
        'mozaik_phone.phone_failure_notification',
    ],
    'postal.coordinate': [
        'mozaik_membership.former_address_id_notification',
        'mozaik_membership.main_address_id_notification',
        'mozaik_address.address_failure_notification',
    ],
    'partners': [
        'mozaik_membership.membership_line_notification',
    ]
}


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _inactive_cascade = True
    _allowed_inactive_link_models = ['res.partner']

    # ready for workflow !
    _enable_wkf = True

    def _get_subtype_ids(
            self, cr, uid, mode, context=None):
        subtype_ids = []
        for xml_id in XML_IDS[mode]:
            splited_id = xml_id.split('.')
            location = splited_id[0]
            xml_id = splited_id[1]
            subtype_ids.append(
                self.pool['ir.model.data'].get_object_reference(
                    cr, uid, location, xml_id)[1])
        return subtype_ids or False

    def _get_followers_assemblies(
            self, cr, uid, pid, context=None):
        context = context or {}
        ia_obj = self.pool['int.assembly']
        int_instance_id = context.get('new_instance_id')
        if not int_instance_id:
            int_instance_id = self.browse(
                cr, uid, pid, context=context).int_instance_id.id
        if not int_instance_id:
            return False
        fol_ids = ia_obj.get_followers_assemblies(
            cr, uid, int_instance_id, context=context)
        return fol_ids or False

    def _subscribe_assemblies(
            self, cr, uid, ids, int_instance_id=None, context=None):
        # compute list of new followers
        ctx = dict(
            context or {},
            new_instance_id=int_instance_id
        )
        fol_ids = []
        for pid in ids:
            fol_ids = self._get_followers_assemblies(
                cr, uid, pid, context=ctx)
            # subscribe assemblies
            subtype_ids = self._get_subtype_ids(
                cr, uid, 'partners', context=context)
            self.message_subscribe(
                cr, uid, [pid], fol_ids,
                subtype_ids=subtype_ids, context=context)
        return fol_ids

    def _update_followers(self, cr, uid, ids, context=None):
        '''
        Update followers list for each partner
        '''
        for partner_id in ids:
            # reset former followers
            self.reset_followers(cr, uid, [partner_id], context=context)
            # subscribe assemblies on partner
            f_partner_ids = self._subscribe_assemblies(
                cr, uid, [partner_id], context=context)

            # subscribe assemblies on coordinates
            domain = [('partner_id', '=', partner_id)]
            for prefix in ['email', 'postal', 'phone']:
                obj = self.pool['%s.coordinate' % prefix]
                res_ids = obj.search(
                    cr, uid, domain, context=context)
                if res_ids:
                    obj.reset_followers(
                        cr, uid, res_ids, except_fol_ids=[partner_id],
                        context=context)
                    obj._update_followers(
                        cr, uid, res_ids, fol_ids=f_partner_ids,
                        context=context)

        return True

    @api.cr_uid_id_context
    def _change_instance(self, cr, uid, pid, new_instance_id, context=None):
        """
        Update instance of partner
        """
        # update partner and send changing instance notification
        vals = {
            'int_instance_id': new_instance_id,
        }
        self.write(cr, uid, [pid], vals, context=context)

    def _generate_membership_reference(self, cr, uid, partner_id,
                                       ref_date=None, context=None):
        """
        This method is intended to be overriden regarding
        locale conventions.
        Here is an arbitrary convention: "MS: YYYY/id"
        """
        ref_date = ref_date or date.today().year
        ref = 'MS: %s/%s' % (ref_date, partner_id)
        return ref

    def _update_user_partner(self, cr, uid, partner, vals, context=None):
        """
        When creating a user from a partner,
        give a first value to its int_instance_m2m_ids collection
        """
        vals = vals or {}
        vals['int_instance_m2m_ids'] = [(6, 0, [partner.int_instance_id.id])]
        super(res_partner, self)._update_user_partner(
            cr, uid, partner, vals, context=context)

    def _get_product_id(self, cr, uid, ids, name, arg, context=None):
        res = {}
        ml_values = self.pool['membership.line'].search_read(
            cr, uid, [('partner_id', 'in', ids), ('active', '=', True)],
            ['partner_id', 'product_id'], context=context)
        for val in ml_values:
            res[val['partner_id'][0]] = val.get('product_id') and\
                val['product_id'][0] or False,
        return res

    def _get_partner_kind(self, cr, uid, ids, name, arg, context=None):
        '''
        Compute the kind of partner, computed field used in ir.rule
        '''
        flds = [
            'is_assembly', 'is_company', 'identifier', 'membership_state_code',
        ]
        res = {}
        vals = self.read(cr, SUPERUSER_ID, ids, flds, context=context)
        for val in vals:
            if val['is_assembly']:
                k = 'a'
            elif not val['identifier']:
                k = 't'
            elif val['is_company']:
                k = 'c'
            elif val['membership_state_code'] == 'without_membership':
                k = 'p'
            else:
                k = 'm'
            res[val['id']] = k
        return res

    _track = {
        'membership_state_id': {
            'mozaik_membership.membership_line_notification':
                lambda self, cr, uid, obj, ctx=None:
                    obj.membership_state_id.code != 'without_membership',
        },
        'int_instance_id': {
            'mozaik_membership.membership_line_notification':
                lambda self, cr, uid, obj, ctx=None:
                    obj.membership_state_id.code != 'without_membership',
        },
    }

    _subscription_store_trigger = {
        'membership.line': (lambda self, cr, uid, ids, context=None:
                            self.pool['membership.line'].get_linked_partners(
                                cr, uid, ids, context=context),
                            ['product_id'], 10),
    }

    _partner_kind_store_trigger = {
        'res.partner': (lambda self, cr, uid, ids, context=None: ids,
                        [
                            'is_assembly', 'is_company',
                            'identifier', 'membership_state_id'
                        ], 10),
    }
    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance', select=True,
            track_visibility='onchange'),
        'int_instance_m2m_ids': fields.many2many(
            'int.instance', 'res_partner_int_instance_rel', id1='partner_id',
            id2='int_instance_id', string='Internal Instances'),
        # membership fields: tracking is done into membership history model
        'membership_line_ids': fields.one2many(
            'membership.line', 'partner_id', string='Memberships'),
        'free_member': fields.boolean('Free Member'),
        'membership_state_id': fields.many2one(
            'membership.state', string='Membership State', select=True,
            track_visibility='onchange'),
        'membership_state_code': fields.related('membership_state_id', 'code',
                                                string='Membership State Code',
                                                type="char", readonly=True),
        'subscription_product_id': fields.function(
            _get_product_id, type='many2one', relation="product.product",
            string='Subscription', store=_subscription_store_trigger),
        'kind': fields.function(
            _get_partner_kind, string='Partner Kind', type='selection',
            selection=AVAILABLE_PARTNER_KINDS,
            store=_partner_kind_store_trigger),
        'accepted_date': fields.date('Accepted Date'),
        'decline_payment_date': fields.date('Decline Payment Date'),
        'rejected_date': fields.date('Rejected Date'),
        'resignation_date': fields.date('Resignation Date'),
        'exclusion_date': fields.date('Exclusion Date'),

        'del_doc_date': fields.date(
            'Welcome Documents Sent Date', track_visibility='onchange'),
        'del_mem_card_date': fields.date('Member Card Sent Date',
                                         track_visibility='onchange'),
        'reference': fields.char('Reference'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
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

    def create(self, cr, uid, vals, context=None):
        '''
        If partner has an identifier then update its followers
        '''
        if not vals.get('is_company', False):
            # Force the state here to avoid a security alert
            # when creating the workflow and updating the first time
            # the state of the new partner
            state_obj = self.pool['membership.state']
            vals.update({
                'membership_state_id': state_obj._state_default_get(
                    cr, uid, context=context),
            })
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        if vals.get('identifier', 0) > 0:
            # do not update followers when simulating partner workflow
            # i.e. identifier = -1 (see get_partner_preview method)
            self._update_followers(cr, SUPERUSER_ID, [res], context=context)
        return res

# view methods: onchange, button

    def register_free_membership(self, cr, uid, ids, context=None):
        '''
        Accept free subscription as membership payment
        '''
        # Accept membership
        self.pool['res.partner'].signal_workflow(
            cr, uid, ids, 'paid', context=context)
        # Get free subscription
        imd_obj = self.pool['ir.model.data']
        free_prd_id = imd_obj.xmlid_to_res_id(
            cr, uid, 'mozaik_membership.membership_product_free')
        vals = {
            'product_id': free_prd_id,
            'price': 0.0,
        }
        # Force free subscription
        for partner in self.browse(cr, uid, ids, context=context):
            partner.current_membership_line_id.write(vals)

    def decline_payment(self, cr, uid, ids, context=None):
        ctx = dict(context or {}, do_not_track_twice=True)
        today = fields.date.today()
        return self.write(cr, uid, ids, {'decline_payment_date': today},
                          context=ctx)

    def reject(self, cr, uid, ids, context=None):
        ctx = dict(context or {}, do_not_track_twice=True)
        today = fields.date.today()
        return self.write(cr, uid, ids, {'rejected_date': today},
                          context=ctx)

    @api.multi
    def _exclude_or_resign(self, field):
        this = self.with_context(do_not_track_twice=True)
        vals = {field: fields.date.today()}
        this.write(vals)
        res = None
        if self.ids and len(self.ids) == 1:
            # go directly to the co-residency form if any
            coord = self.postal_coordinate_id
            if coord and coord.co_residency_id:
                res = coord.co_residency_id.get_formview_action()
                res = res and res[0] or None
        return res

    def exclude(self, cr, uid, ids, context=None):
        return self._exclude_or_resign(
            cr, uid, ids, 'exclusion_date', context=context)

    def resign(self, cr, uid, ids, context=None):
        return self._exclude_or_resign(
            cr, uid, ids, 'resignation_date', context=context)

    def button_reset_del_doc_date(self, cr, uid, ids, context=None):
        vals = {
            'del_doc_date': False,
        }
        self.write(cr, uid, ids, vals, context=context)

    def button_reset_del_mem_card_date(self, cr, uid, ids, context=None):
        vals = {
            'del_mem_card_date': False,
        }
        self.write(cr, uid, ids, vals, context=context)

    def message_track(self, cr, uid, ids,
                      tracked_fields, initial_values, context=None):
        """
        If a notification has already been sent due to state change
        in the workflow, avoid to sent twice the same notification
        due to state modification tracking
        """
        context = context or {}
        if context.get('do_not_track_twice'):
            tracked_fields.pop('membership_state_id', False)
        super(res_partner, self).message_track(
            cr, uid, ids, tracked_fields, initial_values, context=context)

    def update_membership_reference(self, cr, uid, ids, context=None):
        '''
        Update reference for each partner ids
        '''
        vals = {}
        for partner_id in ids:
            vals['reference'] = self._generate_membership_reference(
                cr, uid, partner_id, context=context)
            self.write(cr, uid, partner_id, vals, context=context)
