# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import base64
import re
from odoo import api, exceptions, fields, models, _
from odoo.fields import first
from odoo.tools import ustr

_logger = logging.getLogger(__name__)
MATCH_EMAIL = re.compile('<(.*)>', re.IGNORECASE)


class DistributionList(models.Model):
    _name = 'distribution.list'
    _inherit = [
        'distribution.list',
        'mail.thread',
        'mail.alias.mixin',
    ]

    mail_forwarding = fields.Boolean(
        default=False,
    )
    newsletter = fields.Boolean(
        default=False,
    )
    partner_path = fields.Char(
        default='id',
    )
    res_partner_opt_out_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_out",
        column1="distribution_list_id",
        column2="partner_id",
        string="Opt-out",
        oldname="opt_out_ids",
    )
    res_partner_opt_in_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_out",
        column1="distribution_list_id",
        column2="partner_id",
        string="Opt-in",
        oldname="opt_in_ids",
    )

    def get_alias_model_name(self, vals):
        return vals.get('alias_model', self._name)

    def get_alias_values(self):
        self.ensure_one()
        values = super().get_alias_values()
        values.update({
            'alias_parent_thread_id': self.id,
            'alias_defaults': {'distribution_list_id': self.id},
        })
        return values

    @api.model
    def _build_alias_name(self, name):
        """
        Build an alias with the name given in parameter and make it unique
        :param name: str
        :return: str
        """
        catchall_alias = self.env['ir.config_parameter'].get_param(
            'mail.catchall.alias')
        if not catchall_alias:
            raise exceptions.MissingError(
                _("Please contact your Administrator to configure a "
                  "'catchall' mail alias"))
        alias = '%s+%s' % (catchall_alias, name)
        alias_name = self.env['mail.alias']._clean_and_make_unique(alias)
        return alias_name

    @api.multi
    def _get_mailing_object(self, email_from, mailing_model=False,
                            email_field='email'):
        """

        :param email_from: str
        :param mailing_model: str
        :param email_field: str
        :return: mailing_model recordset
        """
        email_from = re.findall(MATCH_EMAIL, email_from)
        if email_from:
            email_from = email_from[0]

        if not mailing_model:
            mailing_model = self.dst_model_id.model

        mailing_object = self.env[mailing_model]
        if not email_from:
            return mailing_object.browse()
        domain = [(email_field, '=', email_from)]
        return mailing_object.search(domain, limit=1)

    @api.model
    def _get_attachment(self, data):
        """
        Create an attachment based on given data list
        :param data: list
        :return: ir.attachment recordset
        """
        values = {
            'name': data[0],
            'datas_fname': data[0],
            'datas': base64.encodebytes(data[1].encode()),
            'res_model': 'mail.compose.message',
        }
        return self.env['ir.attachment'].create(values)

    @api.multi
    def _get_mail_compose_message_vals(self, msg, mailing_model=False):
        """

        :param msg: dict
        :param mailing_model: str
        :return: dict
        """
        self.ensure_one()
        if not mailing_model:
            mailing_model = self.dst_model_id.model

        attachments = self.env['ir.attachment']
        for attachment_data in msg.get('attachments', []):
            attachments |= self._get_attachment(attachment_data)
        return {
            'email_from': msg.get('from', False),
            'composition_mode': 'mass_mail',
            'subject': msg.get('subject', False),
            'body': msg.get('body', False),
            'distribution_list_id': self.id,
            'mass_mailing_name': 'Mass Mailing %s' % self.name,
            'model': mailing_model,
            'attachment_ids': [[6, 0, attachments.ids]],
        }

    @api.model
    def _get_opt_res_ids(self, model_name, domain):
        """

        :param model_name: str
        :param domain: list
        :return: model_name recordset
        """
        opt_ids = self.env[model_name].search(domain)
        return opt_ids

    @api.multi
    @api.constrains('mail_forwarding', 'alias_name')
    def _check_forwarding(self):
        """
        False if alias_name and mail_forwarding are incompatible
        True otherwise
        :return:
        """
        if self.filtered(lambda r: r.mail_forwarding != bool(r.alias_name)):
            raise exceptions.ValidationError(
                _("An alias is mandatory for mail forwarding, forbidden "
                  "otherwise"))

    @api.model
    def create(self, vals):
        """
        Define into context:
        - alias_model_name with current model name
        - alias_parent_model_name with current model name
        and pop the mail_forwarding from vals
        :param vals: dict
        :return: self recordset
        """
        context = self.env.context.copy()
        context.update({
            'alias_model_name': self._name,
            'alias_parent_model_name': self._name,
        })
        if not vals.get('mail_forwarding'):
            vals.pop('alias_name', False)
        return super(
            DistributionList, self.with_context(context)).create(vals)

    @api.multi
    def write(self, vals):
        """

        :param vals: dict
        :return: bool
        """
        if not vals.get('mail_forwarding', True):
            vals.update({
                'alias_name': False,
            })
        return super().write(vals)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
        Override the native mail.thread method to not create a document anymore
        for distribution list object.
        New Behavior is to forward the current message `msg_dict` to all
        recipients of the distribution list
        :param msg_dict: dict
        :param custom_values: dict
        :return: self recordset
        """
        custom_values = custom_values or {}
        dist_list_id = custom_values.get('distribution_list_id')
        dist_list = self.browse()
        if not dist_list_id:
            param = ' for alias %s' % msg_dict.get('to', '')
            _logger.warning('Mail Forwarding not available: no distribution '
                            'list specified%s', param)
        else:
            dist_list = self.browse(dist_list_id)
            if dist_list.mail_forwarding:
                dist_list._distribution_list_forwarding(msg_dict)
            else:
                _logger.warning(
                    'Mail Forwarding not allowed for distribution list %s: '
                    'Email "%s" send however a message to it',
                    dist_list_id, msg_dict.get('email_from', '??'))
        return dist_list

    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        """
        Do not allow update case of mail forwarding
        :param msg_dict: dict
        :param update_vals: dict
        :return: bool
        """
        return True

    @api.multi
    def _get_target_from_distribution_list(self, safe_mode=True):
        """
        manage opt in/out.
        If the distribution list are newsletter and also have a parther_path
        then
        * remove all res_ids that contains a partner id into the opt_out_ids
        * add to res_ids all partner id into the opt_in_ids
        :param safe_mode: bool
        :return: target recordset
        """
        self.ensure_one()
        targets = super()._get_target_from_distribution_list(
            safe_mode=safe_mode)
        if self.newsletter and self.partner_path:
            partner_path = self.partner_path
            model = self.dst_model_id.model
            # opt in
            partners = self.res_partner_opt_in_ids
            domain = [(partner_path, 'in', partners.ids)]
            targets |= self._get_opt_res_ids(model, domain)

            # opt out
            partners = self.res_partner_opt_out_ids
            domain = [(partner_path, 'in', partners.ids)]
            targets -= self._get_opt_res_ids(model, domain)

        return targets

    @api.multi
    def _update_opt(self, partners, mode='out'):
        """
        update the list of opt out/in
        :param partners: res.partner recordset
        :param mode: str
        :return: bool
        """
        self.ensure_one()
        if mode not in ['in', 'out']:
            raise exceptions.ValidationError(
                _('Mode "%s" is not a valid mode') % mode)
        target_field = 'res_partner_opt_%s_ids' % mode
        if partners and hasattr(self, target_field):
            opt_val = [(4, p.id, False) for p in partners]
            if opt_val:
                vals = {
                    target_field: opt_val,
                }
                return self.write(vals)
        return False

    @api.multi
    def _distribution_list_forwarding(self, msg):
        """
        Create a 'mail.compose.message' depending of the message msg and then
        send a mail with this composer to the resulting ids of the
        distribution list 'dl_id'
        If the subject message starts with the code define on parameters
        (key = distribution.list.mass.mailing.test) (case-insensitive),
        so the dest. email become the sender
        :param msg:
        :return:
        """
        target = self._get_mailing_object(msg.get('email_from', ''))
        subject = msg.get('subject')
        test_code = ustr(self.env['ir.config_parameter'].get_param(
            "distribution.list.mass.mailing.test", default="TEST"))
        self_ctx = self
        if len(target) != 1:
            _logger.warning(
                'An unknown or ambiguous email (%s) '
                'tries to forward a mail through a distribution list',
                msg.get('email_from'))
        elif subject.upper().startswith(test_code.upper()):
            msg.update({
                # Do not use the replace because it's case-sensitive
                'subject': subject[len(test_code):],
            })
            self_ctx = self.with_context(
                active_id=target.id, active_ids=target.ids,
                active_model=target._name, dl_computed=True)
        else:
            self_ctx = self.with_context(dl_computed=False)
        context = self_ctx.env.context
        active_ids = context.get('active_ids', [])
        dl_computed = context.get('dl_computed', True)
        if active_ids or not dl_computed:
            mail_composer_obj = self_ctx.env['mail.compose.message']
            # get composer values to create wizard
            mail_composer_vals = self_ctx._get_mail_compose_message_vals(msg)
            mail_composer = mail_composer_obj.create(mail_composer_vals)
            mail_composer.send_mail()

    @api.onchange('mail_forwarding', 'alias_name', 'name')
    def _onchange_mail_forwarding(self):
        if self.mail_forwarding and not self.alias_name and self.name:
            self.alias_name = self._build_alias_name(self.name)
