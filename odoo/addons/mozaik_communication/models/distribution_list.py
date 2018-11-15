# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import html
from email.utils import formataddr
from odoo import api, exceptions, fields, models, _
from odoo.osv import expression
from odoo.fields import first
from odoo.addons.user_bypass_security.fields import Many2manySudoRead

_logger = logging.getLogger(__name__)


class DistributionList(models.Model):

    _name = "distribution.list"
    _inherit = [
        'mozaik.abstract.model',
        'distribution.list',
    ]
    _unicity_keys = 'name, int_instance_id'

    name = fields.Char(
        track_visibility='onchange',
    )
    public = fields.Boolean(
        track_visibility='onchange',
    )
    res_users_ids = Many2manySudoRead(
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
        string="Diffusion partner",
        index=True,
        track_visibility='onchange',
    )
    res_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_rel",
        column1="distribution_list_id",
        column2="res_partner_id",
        string="Allowed partners",
    )
    code = fields.Char(
        track_visibility='onchange',
    )
    partner_path = fields.Char(
        default="partner_id",
    )

    _sql_constraints = [
        ('unique_code', 'unique (code)', 'Code already used!'),
    ]

    @api.model
    def _get_dst_model_names(self):
        """
        Get the list of available model name
        :return: list of string
        """
        res = super()._get_dst_model_names()
        return res + ['virtual.target']

    @api.model
    def _get_mailing_object(
            self, email_from,
            mailing_model='email.coordinate', email_field='email'):
        """
        Get email coordinate(s) from a sanitized email
        :param email_from: str
        :param mailing_model: str
        :param email_field: str
        :return: email coordinate recordset
        """
        email_from = self.env['email.coordinate']._sanitize_email(email_from)
        return super()._get_mailing_object(
            email_from, mailing_model=mailing_model,
            email_field=email_field)

    @api.multi
    def _get_mail_compose_message_vals(self, msg, mailing_model=False):
        """
        Prepare values for a composer from an incomming message
        :param msg: incomming message str
        :param mailing_model: str
        :param email_field: str
        :return: composer dict
        """
        self.ensure_one()
        result = super()._get_mail_compose_message_vals(
            msg, mailing_model='email.coordinate')
        if result.get('mass_mailing_name') and result.get('subject'):
            result.update({
                'mass_mailing_name': result['subject'],
            })
        if self.partner_id.email:
            result.update({
                'email_from': formataddr(
                    (self.partner_id.name, self.partner_id.email)),
            })
        return result

    @api.onchange('newsletter')
    def _onchange_newsletter(self):
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
        return super()._get_opt_res_ids(model_name, domain, in_mode)

    @api.multi
    def _distribution_list_forwarding(self, msg):
        """
        check if the associated user of the email_coordinate (found with
        msg['email_from']) is an owner of the distribution list
        If user is into the owners then call super with uid=found_user_id
        :param msg:
        :return: Boolean
        """
        self.ensure_one()
        res = False
        partner = self.env['res.partner'].browse()
        user = self.env['res.users'].browse()
        is_partner_allowed = False
        has_visibility = False
        email_from = msg.get('email_from')
        noway = _('No unique coordinate found with address: %s') % email_from
        coordinate = self._get_mailing_object(email_from)
        if len(coordinate) == 1:
            params = (coordinate.email, coordinate.id,
                      coordinate.partner_id.display_name)
            noway = _('Coordinate %s(%s) of %s is not main') % params
            if coordinate.is_main:
                partner = coordinate.partner_id
        if partner:
            noway = _('Partner %s is not an owner nor '
                      'an allowed partner') % partner.display_name
            if partner in self.res_partner_ids:
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
                # business logic continue with this user
                self_sudo = self.sudo(user.id)
                # Force access rules
                self_sudo.check_access_rule('read')
                has_visibility = True
            except exceptions.AccessError:
                params = (user.name, user.id, self.name, self.id)
                noway = _('User %s(%s) has no visibility on list '
                          '%s(%s)') % params
        if has_visibility:
            dom = []
            if self.dst_model_id.model == 'virtual.target':
                dom.append(('email_unauthorized', '=', False))
            self = self_sudo.with_context(
                main_object_field='email_coordinate_id',
                main_target_model='email.coordinate',
                main_object_domain=dom,
                additional_res_ids=coordinate.ids,
                async_send_mail=True,
            )
            res = super()._distribution_list_forwarding(msg)
        else:
            _logger.info('Mail forwarding aborted. Reason: %s', noway)
            self._reply_error_to_owners(msg, noway)
        return res

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
    def action_show_result_without_coordinate(self):
        """
        Show the result of the distribution list without coordinate
        :return: dict/action
        """
        self.ensure_one()
        result = self.with_context(active_test=False).action_show_result()
        result.update({
            'name': _('Result of %s without coordinate') % self.name
        })
        domain = result.get('domain', [])
        domain = expression.AND([domain, [('active', '=', False)]])
        result.update({
            'domain': domain,
        })
        return result

    @api.multi
    def write(self, vals):
        """
        Destroy code when invalidating distribution lists
        :param vals: dict
        :return: bool
        """
        if not vals.get('active', True):
            vals.update({
                'code': False,
            })
        res = super().write(vals)
        return res
