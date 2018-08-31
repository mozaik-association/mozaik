# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import html
from email.utils import formataddr
from odoo import api, exceptions, fields, models, tools, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.fields import first

_logger = logging.getLogger(__name__)


class DistributionList(models.Model):

    _name = "distribution.list"
    _inherit = [
        'distribution.list',
        'mozaik.abstract.model',
    ]
    _order = 'name'
    _unicity_keys = 'name, int_instance_id'

    name = fields.Char(
        required=True,
        track_visibility='onchange',
    )
    public = fields.Boolean(
        track_visibility='onchange',
    )
    res_users_ids = fields.Many2many(
        comodel_name="res.users",
        relation="dist_list_res_users_rel",
        column1="dist_list_id",
        column2="res_users_id",
        string="Owners",
        required=True,
        default=lambda self: self.env.user,
    )
    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal instance",
        index=True,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner diffusion",
        index=True,
        track_visibility='onchange',
    )
    res_partner_m2m_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_rel",
        column1="distribution_list_id",
        column2="res_partner_id",
        string="Allowed partners",
    )
    code = fields.Char(
        track_visibility='onchange',
    )
    dst_model_id = fields.Many2one(
        default=lambda self: self.env.ref(
            "mozaik_communication.model_virtual_target"),
    )
    bridge_field = fields.Char(
        default="common_id",
    )
    partner_path = fields.Char(
        default="partner_id",
    )
    note = fields.Text(
        track_visibility='onchange',
    )
    # No More Global Unique Name
    _sql_constraints = [
        ('unique_code', 'unique (code)', 'Code already used!'),
    ]

    @api.model_cr
    def init(self):
        """
        Drop the constraint about unique name
        :return:
        """
        result = super(DistributionList, self).init()
        tools.drop_constraint(
            self.env.cr, self._table, "constraint_uniq_name")
        return result

    @api.model
    def _get_mailing_object(self, email_from, mailing_model=False,
                            email_field='email'):
        """

        :param email_from: str
        :param mailing_model: str
        :param email_field: str
        :return: mailing_model recordset
        """
        mailing_model = 'email.coordinate'
        email_from = self.env[mailing_model]._sanitize_email(email_from)
        return super(DistributionList, self)._get_mailing_object(
            email_from, mailing_model=mailing_model,
            email_field=email_field)

    @api.multi
    def _get_mail_compose_message_vals(self, msg, mailing_model=False):
        self.ensure_one()
        result = super(DistributionList, self)._get_mail_compose_message_vals(
            msg, mailing_model='email.coordinate')
        if result.get('mass_mailing_name') and result.get('subject'):
            result.update({
                'mass_mailing_name': result.get('subject'),
            })
        if self.partner_id.email:
            result.update({
                'email_from': formataddr(
                    (self.partner_id.name, self.partner_id.email)),
            })
        return result

    @api.multi
    def _get_computed(self, bridge_field, to_be_computed, in_mode):
        self.ensure_one()
        results = super(DistributionList, self)._get_computed(
            bridge_field, to_be_computed, in_mode)
        if not in_mode and results and bridge_field != 'id':
            target_model_name = self.dst_model_id.model
            target_obj = self.env[target_model_name]
            partners = results.mapped("partner_id")
            if partners:
                domain = [
                    ('partner_id', 'in', partners.ids),
                ]
                results = target_obj.search(domain)
        return results

    @api.onchange('dst_model_id')
    def onchange_dst_model(self):
        bridge_field = False
        if self.dst_model_id:
            bridge_field = 'common_id'
            if self.dst_model_id.model == 'res.partner':
                bridge_field = 'id'
        self.bridge_field = bridge_field

    @api.onchange('newsletter')
    def onchange_newsletter(self):
        if not self.newsletter:
            self.code = False

    @api.model
    def _get_opt_res_ids(self, model_name, domain, in_mode):
        """

        :param model_name: str
        :param domain: list
        :param in_mode: bool
        :return: model_name recordset
        """
        if in_mode:
            domain_mail = [
                '|',
                ('email_is_main', '=', True),
                ('email_coordinate_id', '=', False),
            ]
            domain_postal = [
                '|',
                ('postal_is_main', '=', True),
                ('postal_coordinate_id', '=', False),
            ]
            domain = expression.AND(domain, domain_mail, domain_postal)
        return super(DistributionList, self)._get_opt_res_ids(
            model_name, domain, in_mode)

    def distribution_list_forwarding(self, msg):
        """
        check if the associated user of the email_coordinate (found with
        msg['email_from']) is into the owners of the distribution list
        If user is into the owners then call super with uid=found_user_id
        :param msg:
        :return:
        """
        partner = self.env['res.partner'].browse()
        user = self.env['res.users'].browse()
        is_partner_allowed = False
        has_visibility = False
        email_from = msg.get('email_from')
        noway = _('No unique coordinate found with address: %s') % email_from
        coordinate = self._get_mailing_object(email_from)
        if coordinate:
            params = (coordinate.email, coordinate.id,
                      coordinate.partner_id.display_name)
            noway = _('Coordinate %s(%s) of %s is not main') % params
            if coordinate.is_main and coordinate.partner_id:
                partner = coordinate.partner_id
                noway = _('Partner %s is not an owner nor '
                          'an allowed partner') % partner.display_name
                if partner in self.res_partner_m2m_ids:
                    is_partner_allowed = True
                elif partner in self.res_users_ids.mapped("partner_id"):
                    is_partner_allowed = True
            if is_partner_allowed:
                noway = _('Partner %s is not a user') % partner.display_name
                if partner.is_company and partner.responsible_user_id.active:
                    user = partner.responsible_user_id
                else:
                    user = first(partner.user_ids)
            if user:
                try:
                    # Force access rules
                    self.sudo(user.id).name
                    has_visibility = True
                except exceptions.AccessError:
                    params = (user.name, user.id, self.name, self.id)
                    noway = _('User %s(%s) has no visibility on list '
                              '%s(%s)') % params
            if has_visibility:
                context = self.env.context.copy()
                context.update({
                    'email_coordinate_path': 'email',
                    'main_object_field': 'email_coordinate_id',
                    'main_target_model': 'email.coordinate',
                    'main_object_domain': [('email_unauthorized', '=', False)],
                    'additional_res_ids': coordinate.ids,
                })
                return super(DistributionList, self.with_context(context)
                             ).distribution_list_forwarding(msg)
        _logger.info('Mail forwarding aborted. Reason: %s' % noway)
        self._reply_error_to_owners(msg, noway)

    @api.multi
    def _reply_error_to_owners(self, msg, reason):
        """
        Send an email to distribution list owners to explain
        the forwarding no way
        :param msg:
        :param reason:
        :return:
        """
        self.ensure_one()
        # Remove navigation history: maybe we're coming from partner
        ctx = self.env.context.copy()
        for key in ('active_model', 'active_id', 'active_ids'):
            ctx.pop(key, None)

        composer_obj = self.env['mail.compose.message'].with_context(ctx)
        email_from = html.escape(msg.get('email_from'))
        reason = html.escape(reason)
        name = html.escape(self.name)
        body = _('<p>Distribution List: %s</p>'
                 '<p>Sender: %s</p>'
                 '<p>Failure Reason: %s</p>') % (name, email_from, reason),
        vals = {
            'parent_id': False,
            'use_active_domain': False,
            'partner_ids': [
                (6, 0, self.res_users_ids.mapped("partner_id").ids),
            ],
            'notify': False,
            'model': self._name,
            'record_name': self.name,
            'res_id': self.id,
            'email_from': composer_obj._get_default_from(),
            'subject': _('Forwarding Failure: %s') % msg.get('subject', False),
            'body': body,
        }
        composer = composer_obj.create(vals)
        composer.send_mail()

    @api.multi
    def get_all_without_coordinates(self):
        """
        Return all ids corresponding to filters but without any coordinate

        :rtype: {}
        :rparam: dictionary to launch an ir.actions.act_window
        """
        context = self.env.context.copy()
        context.update({
            'active_test': False,
        })
        domain = [
            ('id', 'in', self.ids),
            ('active', '=', False),
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Result of %s') % self.name,
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': self.dst_model_id.model,
            'view_id': False,
            'views': [(False, 'tree')],
            'domain': domain,
            'context': context,
            'target': 'current',
        }

    def action_invalidate(self, vals=None):
        """
        Invalidates distribution lists
        :param vals: dict
        :return: bool
        """
        vals = vals or {}
        vals.update({
            'code': False,
        })
        return super(DistributionList, self).action_invalidate(vals=vals)

    @api.multi
    def write(self, vals):
        """

        :param vals: dict
        :return: bool
        """
        self._create_message_post(vals)
        return super(DistributionList, self).write(vals)

    def _create_message_post(self, vals):
        """

        :param vals: dict
        :return: bool
        """
        if 'alias_name' in vals:
            for record in self:
                old_alias = record.alias_name
                new_alias = vals.get('alias_name')
                domain = record.alias_id.alias_domain
                if new_alias and new_alias != old_alias:
                    subject = _('Alias modified on distribution '
                                'list %s') % record.name
                    msg = "<p>%s,</p><p>%s</p><p>%s<br/>%s</p>"
                    parts = (
                        _('Hello'),
                        _('The alias of the distribution list %s '
                          'has been changed by %s.') % (
                            record.name, record.env.user.name),
                        _('Former alias: %s@%s') % (old_alias, domain),
                        _('<b>New alias</b>: %s@%s') % (new_alias, domain),
                    )
                    body = msg % parts
                    partners = record.res_users_ids.filtered(
                        lambda u: u != self.env.user).mapped("partner_id")
                    partners |= record.res_partner_m2m_ids
                    record.message_post(
                        body=body, subject=subject, partner_ids=partners.ids)
        return True
