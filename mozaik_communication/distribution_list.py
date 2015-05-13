# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from email.utils import formataddr

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class distribution_list(orm.Model):

    _name = "distribution.list"
    _inherit = ['distribution.list', 'mozaik.abstract.model']

    def _get_mailing_object(
            self, cr, uid, dl_id, email_from, mailing_model=False,
            email_field='email', context=None):
        return super(distribution_list, self)._get_mailing_object(
            cr, uid, dl_id, email_from, mailing_model='email.coordinate',
            email_field=email_field, context=context)

    def _get_mail_compose_message_vals(
            self, cr, uid, msg, dl_id, mailing_model=False, context=None):
        res = super(distribution_list, self)._get_mail_compose_message_vals(
            cr, uid, msg, dl_id, mailing_model='email.coordinate',
            context=context)
        dl = self.browse(cr, uid, dl_id, context=context)
        if dl.partner_id and dl.partner_id.email:
            res['email_from'] = formataddr(
                (dl.partner_id.name, dl.partner_id.email))
        return res

    _columns = {
        'name': fields.char(
            string='Name', required=True, track_visibility='onchange'),
        'public': fields.boolean('Public', track_visibility='onchange'),
        'res_users_ids': fields.many2many(
            'res.users', 'dist_list_res_users_rel',
            id1='dist_list_id', id2='res_users_id',
            string='Owners', required=True),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            select=True, track_visibility='onchange'),
        'partner_id': fields.many2one(
            'res.partner', string='Partner Diffusion',
            select=True, track_visibility='onchange'),
    }

    _defaults = {
        'res_users_ids': lambda self, cr, uid, c: [uid],
        'dst_model_id': lambda self, cr, uid, c:
            self.pool['ir.model'].search(
                cr, uid, [('model', '=', 'virtual.target')])[0],
        'bridge_field': 'common_id',
        'partner_path': 'partner_id',
    }

# constraints

    # No More Unique Name For distribution list
    _sql_constraints = [('unique_name_by_company', 'check(1=1)', '')]

    _unicity_keys = 'name, int_instance_id'

# view methods: onchange, button

    def onchange_dst_model(self, cr, uid, ids, dst_model_id, context=None):
        res = {}
        bridge_field = False
        if dst_model_id:
            model = self.pool.get('ir.model').browse(
                cr, uid, dst_model_id, context=context)
            if model.model == 'res.partner':
                bridge_field = 'id'
            else:
                bridge_field = 'common_id'
        res['value'] = {'bridge_field': bridge_field}
        return res

# public methods

    def get_distribution_list_from_filters(self, cr, uid, ids, context=None):
        domain = [
            '|',
            ('to_include_distribution_list_line_ids', 'in', ids),
            ('to_exclude_distribution_list_line_ids', 'in', ids),
        ]
        res_ids = self.search(cr, uid, domain, context=context)
        return res_ids

    def distribution_list_forwarding(self, cr, uid, msg, dl_id, context=None):
        """
        check if the associated user of the email_coordinate (found with
        msg['email_from']) is into the owners of the distribution list
        If user is into the owners then call super with uid=found_user_id
        """
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['email_coordinate_path'] = 'email'

        coordinate_ids = self._get_mailing_object(
            cr, uid, dl_id, msg['email_from'], context=context)
        if coordinate_ids:
            coo_values = self.pool['email.coordinate'].read(
                cr, uid, coordinate_ids[0], ['partner_id'], context=context)
            partner_id = coo_values.get('partner_id') and \
                coo_values['partner_id'][0] or False
            if partner_id:
                user_ids = self.pool['res.users'].search(
                    cr, uid, [('partner_id', '=', partner_id)],
                    context=context)
                user_id = user_ids and user_ids[0] or False
                if user_id:
                    dl_values = self.read(
                        cr, uid, dl_id, ['res_users_ids'], context=context)
                    owner_ids = dl_values.get('res_users_ids', False)
                    if user_id in owner_ids:
                        ctx['field_main_object'] = 'email_coordinate_id'
                        return super(distribution_list, self).\
                            distribution_list_forwarding(
                                cr, user_id, msg, dl_id, context=ctx)
        return

    def _register_hook(self, cr):
        super(distribution_list, self)._register_hook(cr)
        self._fields['note'].track_visibility = 'onchange'
        pass

    def get_all_without_coordinates(self, cr, uid, ids, context=None):
        """
        Return all ids corresponding to filters but without any coordinate

        :rtype: {}
        :rparam: dictionary to launch an ir.actions.act_window
        """
        context = {} if context is None else context
        context['active_test'] = False
        dl = self.browse(cr, uid, ids, context=context)[0]
        res_ids = self.get_ids_from_distribution_list(cr, uid, ids,
                                                      context=context)
        domain = "[['id', 'in', %s]"\
                 ",['active', '=', False]]" % res_ids
        return {'type': 'ir.actions.act_window',
                'name': _('Result of %s') % dl.name,
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': dl.dst_model_id.model,
                'view_id': False,
                'views': [(False, 'tree')],
                'domain': domain,
                'target': 'new',
                }


class distribution_list_line(orm.Model):

    _name = "distribution.list.line"
    _inherit = ['distribution.list.line', 'mozaik.abstract.model']

    _columns = {
        'name': fields.char(
            string='Name', required=True, track_visibility='onchange'),
        'domain': fields.text(
            string='Expression', required=True, track_visibility='onchange'),
        'src_model_id': fields.many2one(
            'ir.model', string='Model', required=True, select=True,
            domain=[('model', 'in', [
                'virtual.partner.instance',
                'virtual.partner.membership',
                'virtual.partner.event',
                'virtual.partner.relation',
                'virtual.partner.involvement',
                'virtual.partner.candidature',
                'virtual.partner.mandate',
                'virtual.partner.retrocession',
                'virtual.assembly.instance',
            ])],
            track_visibility='onchange'),
    }

# constraints

    # No More Unique Name For distribution list
    _sql_constraints = [('unique_name_by_company', 'check(1=1)', '')]

    _unicity_keys = 'name, company_id'

# orm methods

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        '''
        Prevent abusive modifications on filter used by some unauthorized
        distribution lists
        '''
        if operation in ['unlink', 'write']:
            dl_obj = self.pool['distribution.list']
            dl_ids = dl_obj.get_distribution_list_from_filters(
                cr, SUPERUSER_ID, ids, context=context)
            dl_obj.check_access_rule(
                cr, uid, dl_ids, operation, context=context)

        super(distribution_list_line, self).check_access_rule(
            cr, uid, ids, operation, context=context)

    def get_list_without_coordinate_from_domain(self,
                                                cr,
                                                uid, ids, context=None):
        context = context or {}
        current_filter = self.browse(cr, uid, ids, context)
        res = super(distribution_list_line, self).get_list_from_domain(
            cr,
            uid,
            ids,
            context=context)
        res['name'] = _('Result of %s Filter without coordinate')\
            % current_filter.name
        no_coord_domain = [('active', '=', False)]
        domain = eval(res['domain'])
        domain.extend(no_coord_domain)
        res['domain'] = str(domain)
        return res
