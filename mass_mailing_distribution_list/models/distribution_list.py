# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import re

from odoo import _, api, exceptions, fields, models
from odoo.tools import ustr

_logger = logging.getLogger(__name__)
MATCH_EMAIL = re.compile("<(.*)>", re.IGNORECASE)


class DistributionList(models.Model):
    _name = "distribution.list"
    _inherit = [
        "distribution.list",
        "mail.thread",
        "mail.alias.mixin",
    ]

    mail_forwarding = fields.Boolean(
        default=False,
    )
    newsletter = fields.Boolean(
        default=False,
    )
    partner_path = fields.Char(
        compute="_compute_partner_path", store=True, readonly=False
    )
    res_partner_opt_out_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_out",
        column1="distribution_list_id",
        column2="partner_id",
        string="Opt-Out",
    )
    res_partner_opt_in_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_in",
        column1="distribution_list_id",
        column2="partner_id",
        string="Opt-In",
    )

    @api.depends("dst_model_id")
    def _compute_partner_path(self):
        """
        If dst_model_id == "res.partner": partner_path = "id",
        Elif dst_model_id has a field partner_id, then
        partner_path = "partner_id".
        Else partner_path = False.
        """
        for distribution_list in self:
            distribution_list.partner_path = False
            if distribution_list.dst_model_id:
                if distribution_list.dst_model_id.model == "res.partner":
                    distribution_list.partner_path = "id"
                elif "partner_id" in distribution_list.dst_model_id.field_id.mapped(
                    "name"
                ):
                    distribution_list.partner_path = "partner_id"

    @api.constrains("partner_path")
    def _check_partner_path(self):
        for distribution_list in self:
            if (
                distribution_list.partner_path
                not in distribution_list.dst_model_id.field_id.mapped("name")
            ):
                raise exceptions.ValidationError(
                    _(
                        "Partner Path is not valid: this field doesn't exist on model '%s'"
                        % distribution_list.dst_model_id.name
                    )
                )

    @api.model
    def _build_alias_name(self, name):
        """
        Build an alias with the name given in parameter and make it unique
        :param name: str
        :return: str
        """
        catchall_alias = (
            self.env["ir.config_parameter"].sudo().get_param("mail.catchall.alias")
        )
        if not catchall_alias:
            raise exceptions.MissingError(
                _(
                    "Please contact your Administrator to configure a "
                    "'catchall' mail alias"
                )
            )
        alias = "%s+%s" % (catchall_alias, name)
        alias_name = self.env["mail.alias"]._clean_and_check_unique(alias)
        return alias_name

    def _get_mailing_object(self, email_from, mailing_model=False, email_field="email"):
        """
        Get records related to an email (typically partners)
        :param email_from: str
        :param mailing_model: str
        :param email_field: str
        :return: mailing_model recordset
        """
        res = re.findall(MATCH_EMAIL, email_from)
        if res:
            email_from = res[0]

        if not mailing_model:
            mailing_model = self.dst_model_id.model

        mailing_object = self.env[mailing_model]
        if not email_from:
            return mailing_object.browse()
        domain = [(email_field, "=", email_from)]
        return mailing_object.search(domain)

    @api.model
    def _get_attachment(self, data):
        """
        Create an attachment based on given data list
        :param data: list
        :return: ir.attachment recordset
        """
        values = {
            "name": data[0],
            "datas": base64.encodebytes(data[1].encode()),
            "res_model": "mail.compose.message",
        }
        return self.env["ir.attachment"].create(values)

    def _get_mail_compose_message_vals(self, msg, mailing_model=False):
        """
        Prepare values for a composer from an incomming message
        :param msg: incomming message str
        :param mailing_model: str
        :param email_field: str
        :return: composer dict
        """
        self.ensure_one()
        if not mailing_model:
            mailing_model = self.dst_model_id.model

        attachments = self.env["ir.attachment"]
        for attachment_data in msg.get("attachments", []):
            attachments |= self._get_attachment(attachment_data)
        return {
            "email_from": msg.get("email_from", False),
            "composition_mode": "mass_mail",
            "subject": msg.get("subject", False),
            "body": msg.get("body", False),
            "distribution_list_id": self.id,
            "mass_mailing_name": "Mass Mailing %s" % self.name,
            "model": mailing_model,
            "attachment_ids": [[6, 0, attachments.ids]],
        }

    def _get_opt_res_ids(self, domain):
        """
        Get destination model opt/in opt/out records
        :param domain: list
        :return: dst model recordset
        """
        self.ensure_one()
        opt_ids = self.env[self.dst_model_id.model].search(domain)
        return opt_ids

    @api.constrains("mail_forwarding", "alias_name")
    def _check_forwarding(self):
        """
        False if alias_name and mail_forwarding are incompatible
        True otherwise
        :return:
        """
        if self.filtered(lambda r: r.mail_forwarding != bool(r.alias_name)):
            raise exceptions.ValidationError(
                _("An alias is mandatory for mail forwarding, forbidden " "otherwise")
            )

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
        if not vals.get("mail_forwarding"):
            vals.pop("alias_name", False)
        dist_model = self.env.ref("distribution_list.model_distribution_list")
        alias = self.env["mail.alias"].create(
            {
                "alias_parent_model_id": dist_model.id,
                "alias_model_id": dist_model.id,
                "alias_name": vals.get("alias_name", False),
            }
        )
        vals["alias_id"] = alias.id
        distribution_list = super(DistributionList, self).create(vals)
        distribution_list.alias_defaults = {
            "distribution_list_id": distribution_list.id
        }
        return distribution_list

    def write(self, vals):
        """

        :param vals: dict
        :return: bool
        """
        if not vals.get("mail_forwarding", True):
            vals.update(
                {
                    "alias_name": False,
                }
            )

        # write it first on the mail.alias, because _check_forwarding
        # constraint doesnt' like it otherwise
        if vals.get("alias_name"):
            self.mapped("alias_id").write({"alias_name": vals.get("alias_name")})
        return super().write(vals)

    def unlink(self):
        # unlink all autogenerated mail.alias not needed anymore
        mail_aliases = self.mapped("alias_id")
        res = super(DistributionList, self).unlink()
        distribution_lists = self.search([("alias_id", "in", mail_aliases.ids)])
        (mail_aliases - distribution_lists.mapped("alias_id")).unlink()
        return res

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
        dist_list_id = custom_values.get("distribution_list_id")
        dist_list = self.browse()
        if not dist_list_id:
            param = " for alias %s" % msg_dict.get("to", "")
            _logger.warning(
                "Mail Forwarding not available: no distribution " "list specified%s",
                param,
            )
        else:
            dist_list = self.browse(dist_list_id)
            if dist_list.mail_forwarding:
                dist_list._distribution_list_forwarding(msg_dict)
            else:
                _logger.warning(
                    "Mail Forwarding not allowed for distribution list %s: "
                    'Email "%s" send however a message to it',
                    dist_list_id,
                    msg_dict.get("email_from", "??"),
                )
        return dist_list

    def message_update(self, msg_dict, update_vals=None):
        """
        Do not allow update case of mail forwarding
        :param msg_dict: dict
        :param update_vals: dict
        :return: bool
        """
        return True

    def _get_target_from_distribution_list(self):
        """
        manage opt in/out.
        If the distribution list is a newsletter and has a parther_path then:
        * remove all res_ids that contains a partner id into the opt_out_ids
        * add to res_ids all partner id into the opt_in_ids
        :return: target recordset
        """
        self.ensure_one()
        targets = super()._get_target_from_distribution_list()
        if self.newsletter and self.partner_path:
            partner_path = self.partner_path
            # opt in
            partners = self.res_partner_opt_in_ids
            domain = [(partner_path, "in", partners.ids)]
            targets |= self._get_opt_res_ids(domain)

            # opt out
            partners = self.res_partner_opt_out_ids
            domain = [(partner_path, "in", partners.ids)]
            targets -= self._get_opt_res_ids(domain)

        return targets

    def _update_opt(self, partner_ids, mode="out"):
        """
        Update list of opt out/in
        :param partners: list of target model ids
        :param mode: str
        :return: bool
        """
        self.ensure_one()
        if mode not in ["in", "out"]:
            raise exceptions.ValidationError(_('Mode "%s" is not a valid mode') % mode)
        if partner_ids and self.partner_path:
            partner_ids = (
                self.env[self.dst_model_id.model]
                .browse(partner_ids)
                .mapped(self.partner_path)
            )
        if partner_ids:
            vals = {}
            for opt in ["in", "out"]:
                opt_field = "res_partner_opt_%s_ids" % opt
                opt_val = [(4 if mode == opt else 3, pid) for pid in partner_ids]
                vals.update(
                    {
                        opt_field: opt_val,
                    }
                )
            res = self.write(vals)
            return res
        return False

    def _distribution_list_forwarding(self, msg):
        """
        Create a 'mail.compose.message' depending of the message msg and then
        send a mail with this composer to the resulting ids of the
        distribution list 'dl_id'
        If the subject message starts with the code define on parameters
        (key = distribution.list.mass.mailing.test) (case-insensitive),
        so the dest. email become the sender
        :param msg:
        :return: Boolean
        """
        res = False
        target = self._get_mailing_object(msg.get("email_from", ""))
        subject = msg.get("subject")
        test_code = ustr(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("distribution.list.mass.mailing.test", default="AAAAAA")
        )
        self_ctx = self
        if len(target) != 1:
            _logger.warning(
                "An unknown or ambiguous email (%s) "
                "tries to forward a mail through a distribution list",
                msg.get("email_from"),
            )
        elif subject.upper().startswith(test_code.upper()):
            msg.update(
                {
                    # Do not use the replace because it's case-sensitive
                    "subject": subject[len(test_code) :],
                }
            )
            self_ctx = self.with_context(
                active_id=target.id,
                active_ids=target.ids,
                active_model=target._name,
                dl_computed=True,
            )
        else:
            self_ctx = self.with_context(dl_computed=False)
        context = self_ctx.env.context
        active_ids = context.get("active_ids", [])
        dl_computed = context.get("dl_computed", True)
        if active_ids or not dl_computed:
            mail_composer_obj = self_ctx.env["mail.compose.message"]
            # get composer values to create wizard
            mail_composer_vals = self_ctx._get_mail_compose_message_vals(msg)
            mail_composer = mail_composer_obj.create(mail_composer_vals)
            mail_composer.send_mail()
            res = True
        return res

    @api.onchange("mail_forwarding", "alias_name", "name")
    def _onchange_mail_forwarding(self):
        if self.mail_forwarding and not self.alias_name and self.name:
            self.alias_name = self._build_alias_name(self.name)
        if self.mail_forwarding and not self.alias_domain:
            catchall_domain = (
                self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
            )
            if not catchall_domain:
                raise exceptions.MissingError(
                    _(
                        "Please contact your Administrator to configure a "
                        "'catchall' mail domain"
                    )
                )
