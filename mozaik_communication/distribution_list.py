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

import logging
from email.utils import formataddr

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import api, fields as new_fields
from openerp.exceptions import except_orm
from openerp.addons.mozaik_base.base_tools import format_email

_logger = logging.getLogger(__name__)


class distribution_list(orm.Model):

    _name = "distribution.list"
    _inherit = ['distribution.list', 'mozaik.abstract.model']

    def _get_mailing_object(
            self, cr, uid, dl_id, email_from, mailing_model=False,
            email_field='email', context=None):
        email_from = format_email(email_from)
        return super(distribution_list, self)._get_mailing_object(
            cr, uid, dl_id, email_from, mailing_model='email.coordinate',
            email_field=email_field, context=context)

    def _get_mail_compose_message_vals(
            self, cr, uid, msg, dl_id, mailing_model=False, context=None):
        res = super(distribution_list, self)._get_mail_compose_message_vals(
            cr, uid, msg, dl_id, mailing_model='email.coordinate',
            context=context)
        if res.get('mass_mailing_name') and res.get('subject'):
            res['mass_mailing_name'] = res.get('subject')
        dl = self.browse(cr, uid, dl_id, context=context)
        if dl.partner_id and dl.partner_id.email:
            res['email_from'] = formataddr(
                (dl.partner_id.name, dl.partner_id.email))
        return res

    def _get_computed_ids(
            self, cr, uid, dl_id, bridge_field, to_be_computed_ids,
            in_mode, context=None):
        res = super(distribution_list, self)._get_computed_ids(
            cr, uid, dl_id, bridge_field, to_be_computed_ids, in_mode,
            context=context)
        if not in_mode and res and bridge_field != 'id':
            target_model_name = self.browse(
                cr, uid, dl_id).dst_model_id.model
            t_model = self.pool(target_model_name)
            res = list(res)
            t_recs = t_model.read(
                cr, uid, res, ['partner_id'],
                load='_classic_write', context=context)
            p_ids = [r['partner_id'] for r in t_recs]
            if p_ids:
                domain = [
                    ('partner_id', 'in', p_ids)
                ]
                res = t_model.search(cr, uid, domain, context=context)
            res = set(res)
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
        'res_partner_m2m_ids': fields.many2many(
            'res.partner', string='Allowed Partners',
            rel='distribution_list_res_partner_rel',
            column1='distribution_list_id', column2='res_partner_id'),
    }

    code = new_fields.Char('Code', track_visibility='onchange')

    _defaults = {
        'res_users_ids': lambda self, cr, uid, c: [uid],
        'dst_model_id': lambda self, cr, uid, c:
            self.pool['ir.model'].search(
                cr, uid, [('model', '=', 'virtual.target')])[0],
        'bridge_field': 'common_id',
        'partner_path': 'partner_id',
    }

    _order = 'name'

# constraints

    # No More Global Unique Name
    _sql_constraints = [('unique_name_by_company', 'check(1=1)', ''),
                        ('unique_code', 'unique (code)', 'Code already used !')
                        ]

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

    @api.onchange('newsletter')
    def onchange_newsletter(self):
        if not self.newsletter:
            self.code = False

# public methods

    def _get_opt_res_ids(
            self, cr, uid, model_name, domain, in_mode, context=None):
        if in_mode:
            domain.append(('email_is_main', '=', True))
            domain.append(('postal_is_main', '=', True))
        opt_ids = super(distribution_list, self)._get_opt_res_ids(
            cr, uid, model_name, domain, in_mode, context=context)
        return opt_ids

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
        partner_id = False
        user_id = False
        is_partner_allowed = False
        has_visibility = False
        noway = _('No unique coordinate found with address: %s') % \
            msg['email_from']
        coordinate_ids = self._get_mailing_object(
            cr, uid, dl_id, msg['email_from'], context=context)
        if len(coordinate_ids) == 1:
            coo_obj = self.pool['email.coordinate'].browse(
                cr, uid, coordinate_ids[0], context=context)
            noway = _('Coordinate %s(%s) of %s is not main') % (
                coo_obj.email, coo_obj.id, coo_obj.partner_id.display_name)
            if coo_obj.is_main:
                partner_id = coo_obj.partner_id
        if partner_id:
            noway = _('Partner %s is not an owner nor '
                      'an allowed partner') % partner_id.display_name
            dl = self.browse(cr, uid, dl_id, context=context)
            if partner_id.id in [p.id for p in dl.res_partner_m2m_ids]:
                is_partner_allowed = True
            if not is_partner_allowed:
                if partner_id.id in\
                        [p.partner_id.id for p in dl.res_users_ids]:
                    is_partner_allowed = True
        if is_partner_allowed:
            noway = _('Partner %s is not a user') % partner_id.display_name
            res_users_model = self.pool['res.users']
            if partner_id.is_company and partner_id.responsible_user_id:
                user_id = partner_id.responsible_user_id.id
            else:
                domain = [('partner_id', '=', partner_id.id)]
                user_id = res_users_model.search(
                    cr, uid, domain, context=context)
                user_id = res_users_model.browse(
                    cr, uid, user_id and user_id[0] or [], context=context)
        if user_id:
            try:
                self.check_access_rule(
                    cr, user_id.id, [dl_id], 'read', context=context)
                has_visibility = True
            except except_orm:
                noway = _('User %s(%s) has no visibility on list %s(%s)') % \
                    (user_id.name, user_id.id, dl.name, dl.id)
        if has_visibility:
            ctx = dict(context or {},
                       email_coordinate_path='email',
                       main_object_field='email_coordinate_id',
                       main_target_model='email.coordinate',
                       main_object_domain=[('email_unauthorized', '=', False)])
            res_ids = self._get_mailing_object(
                cr, uid, dl_id, msg['email_from'], context=context)
            if res_ids:
                ctx['additional_res_ids'] = res_ids
            return super(distribution_list, self).\
                distribution_list_forwarding(
                cr, user_id.id, msg, dl_id, context=ctx)
        _logger.info('Mail forwarding aborted. Reason: %s' % noway)
        self._reply_error_to_owners(
            cr, uid, [dl_id], msg, noway, context=context)

    @api.multi
    def _reply_error_to_owners(self, msg, reason):
        """
        Send an email to distribution list owners to explain
        the forwarding no way
        """
        self.ensure_one()

        # Remove navigation history: maybe we're coming from partner
        ctx = dict(self.env.context or {})
        for key in ('active_model', 'active_id', 'active_ids'):
            ctx.pop(key, None)

        composer_mod = self.env['mail.compose.message'].with_context(ctx)
        sender = msg['email_from']
        vals = {
            'parent_id': False,
            'use_active_domain': False,
            'partner_ids': [[6, 0, [
                owner.partner_id.id for owner in self.res_users_ids]]],
            'notify': False,
            'model': self._name,
            'record_name': self.name,
            'res_id': self.id,
            'email_from': composer_mod._get_default_from(),
            'subject': _('Forwarding Failure: %s') % msg.get('subject', False),
            'body':
                _('<p>Distribution List: %s</p>'
                  '<p>Sender: %s</p>'
                  '<p>Failure Reason: %s</p>') % (
                    self.name,
                    sender.replace('<', '&lt;').replace('>', '&gt;'),
                    reason),
        }
        composer = composer_mod.create(vals)
        composer.send_mail()

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
                'target': 'current',
                }

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        Invalidates distribution lists
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        vals['code'] = False

        super(distribution_list, self).action_invalidate(
            cr, uid, ids, context=context, vals=vals)

        return True

    @api.multi
    def write(self, vals):
        if 'alias_name' in vals:
            self.ensure_one()
            old_alias = self.alias_name
            new_alias = vals.get('alias_name', False)
            domain = self.alias_id.alias_domain
            if new_alias and new_alias != old_alias:
                subject = _(
                    'Alias modified on distribution list %s') % self.name
                msg = "<p>%s,</p><p>%s</p><p>%s<br/>%s</p>"
                parts = (
                    _('Hello'),
                    _('The alias of the distribution list %s '
                      'has been changed by %s.') % (
                        self.name, self.env.user.name),
                    _('Former alias: %s@%s') % (old_alias, domain),
                    _('<b>New alias</b>: %s@%s') % (new_alias, domain),
                )
                recipient_ids = [
                    user.partner_id.id
                    for user in self.res_users_ids
                    if user.id != self.env.uid
                ]
                recipient_ids += self.res_partner_m2m_ids.ids
                self.message_post(
                    body=msg % parts, subject=subject,
                    partner_ids=recipient_ids)
        return super(distribution_list, self).write(vals)


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
        'distribution_list_in_ids': fields.many2many(
            'distribution.list',
            'include_distribution_list_line_rel',
            'include_distribution_list_line_id',
            'include_distribution_list_id', string="Include in"),
        'distribution_list_out_ids': fields.many2many(
            'distribution.list',
            'exclude_distribution_list_line_rel',
            'exclude_distribution_list_line_id',
            'exclude_distribution_list_id', string="Exclude from"),
    }

    _defaults = {
        'src_model_id': lambda self, cr, uid, c: False,
    }

    _order = 'name'

# constraints

    # No More Global Unique Name
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
        res['name'] = _('Result of %s filter without coordinate')\
            % current_filter.name
        no_coord_domain = [('active', '=', False)]
        domain = eval(res['domain'])
        domain.extend(no_coord_domain)
        res['domain'] = str(domain)
        return res

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        Invalidates distribution list Lines
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        vals['distribution_list_in_ids'] = [(5,)]
        vals['distribution_list_out_ids'] = [(5,)]

        super(distribution_list_line, self).action_invalidate(
            cr, uid, ids, context=context, vals=vals)

        return True
