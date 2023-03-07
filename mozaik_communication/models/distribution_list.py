# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import html
import logging

from odoo import _, api, exceptions, fields, models
from odoo.fields import first
from odoo.osv import expression
from odoo.tools import formataddr

_logger = logging.getLogger(__name__)


class DistributionList(models.Model):

    _name = "distribution.list"
    _inherit = [
        "mozaik.abstract.model",
        "distribution.list",
        "owner.mixin",
    ]
    _unicity_keys = "N/A"

    name = fields.Char(
        tracking=True,
    )
    public = fields.Boolean(
        tracking=True,
    )
    # Owners come from mixin. Rename columns
    res_users_ids = fields.Many2many(
        relation="dist_list_res_users_rel",
        column1="dist_list_id",
        column2="res_users_id",
    )
    int_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Internal instances",
        default=lambda self: self.env.user.int_instance_m2m_ids,
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Diffusion partner",
        index=True,
        tracking=True,
    )
    res_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="distribution_list_res_partner_rel",
        column1="distribution_list_id",
        column2="res_partner_id",
        string="Allowed partners",
    )
    code = fields.Char(
        tracking=True,
    )

    _sql_constraints = [
        ("unique_code", "unique (code)", "Code already used!"),
    ]

    @api.model
    def _get_dst_model_names(self):
        """
        Get the list of available model name
        :return: list of string
        """
        res = super()._get_dst_model_names()
        return res + ["virtual.target"]

    def _get_mailing_mailing_vals(self, msg):
        """
        Prepare values for a composer from an incomming message
        :param msg: incomming message str
        :param mailing_model: str
        :param email_field: str
        :return: composer dict
        """
        self.ensure_one()
        result = super()._get_mailing_mailing_vals(msg)
        result_vals = result[0]
        if result_vals.get("name") and result_vals.get("subject"):
            result_vals.update(
                {
                    "name": result_vals["subject"],
                }
            )
        if self.partner_id.email:
            result_vals.update(
                {
                    "email_from": formataddr(
                        (self.partner_id.name, self.partner_id.email)
                    ),
                }
            )
        result_vals["multi_send_same_email"] = True
        return result

    @api.onchange("newsletter")
    def _onchange_newsletter(self):
        if not self.newsletter:
            self.code = False

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
        partner = self.env["res.partner"].browse()
        user = self.env["res.users"].browse()
        is_partner_allowed = False
        has_visibility = False
        email_from = msg.get("email_from")
        noway = _("No unique coordinate found with address: %s") % email_from
        partner = self._get_mailing_object(email_from)
        if partner._name == "virtual.target":
            partner = partner.mapped("partner_id")
        if partner and len(partner) == 1:
            noway = (
                _("Partner %s is not an owner nor an allowed partner")
                % partner.display_name
            )
            if partner in self.res_partner_ids:
                is_partner_allowed = True
            elif partner in self.res_users_ids.mapped("partner_id"):
                is_partner_allowed = True
        if is_partner_allowed:
            noway = _("Partner %s is not a user") % partner.display_name
            if partner.is_company and partner.responsible_user_id.active:
                user = partner.responsible_user_id
            else:
                user = first(partner.user_ids)
        if user:
            try:
                # business logic continue with this user
                self_sudo = self.with_user(user.id)
                # Force access rules
                self_sudo.check_access_rule("read")
                has_visibility = True
            except exceptions.AccessError:
                params = (user.name, user.id, self.name, self.id)
                noway = _("User %s(%s) has no visibility on list " "%s(%s)") % params
        if has_visibility:
            dom = []
            if self.dst_model_id.model == "virtual.target":
                dom.append(("email_unauthorized", "=", False))
            self = self_sudo.with_context(
                main_target_model="res.partner",
                main_object_domain=dom,
                async_send_mail=True,
            )
            res = super()._distribution_list_forwarding(msg)
        else:
            _logger.info("Mail forwarding aborted. Reason: %s", noway)
            self._reply_error_to_owners(msg, noway)
        return res

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
        for key in ("active_model", "active_id", "active_ids"):
            ctx.pop(key, None)

        composer_obj = self.env["mail.compose.message"].with_context(ctx)
        email_from = html.escape(msg.get("email_from"))
        reason = html.escape(reason)
        name = html.escape(self.name)
        body = _(
            "<p>Distribution List: %s</p>"
            "<p>Sender: %s</p>"
            "<p>Failure Reason: %s</p>"
        ) % (name, email_from, reason)
        recipient_ids = self.res_users_ids.mapped("partner_id").ids
        extra_recipient_ids = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("communication.forwarding_error_recipient_ids")
        )
        if extra_recipient_ids:
            recipient_ids += [
                int(i) for i in extra_recipient_ids.replace(" ", "").split(",") if i
            ]
        vals = {
            "parent_id": False,
            "use_active_domain": False,
            "partner_ids": [(6, 0, recipient_ids)],
            "notify": False,
            "model": self._name,
            "record_name": self.name,
            "res_id": self.id,
            "email_from": formataddr((self.env.user.name, self.env.user.email)),
            "subject": _("Forwarding Failure: %s") % msg.get("subject", False),
            "body": body,
        }
        composer = composer_obj.create(vals)
        composer.send_mail()

    def action_show_result_without_coordinate(self):
        """
        Show the result of the distribution list without coordinate
        :return: dict/action
        """
        self.ensure_one()
        result = self.with_context(active_test=False).action_show_result()
        result.update({"name": _("Result of %s without coordinate") % self.name})
        domain = result.get("domain", [])
        domain = expression.AND([domain, [("active", "=", False)]])
        result.update(
            {
                "domain": domain,
            }
        )
        return result

    def write(self, vals):
        """
        Destroy code when invalidating distribution lists
        :param vals: dict
        :return: bool
        """
        if not vals.get("active", True):
            vals.update(
                {
                    "code": False,
                }
            )
        res = super().write(vals)
        return res

    def _get_partner_from(self):
        """
        Get partner from distribution list
        :return: res.partner recordset
        """
        partners = self.env["res.partner"].browse()
        if len(self) != 1:
            return partners
        # first: the sender partner
        partners |= self.partner_id
        # than: the requestor user
        if (
            self.env.user.partner_id in self.res_partner_ids
            or self.env.user in self.res_users_ids
        ):
            partners |= self.env.user.partner_id
        # finally: all owners and allowed partners that are legal persons
        partners |= self.res_partner_ids.filtered(lambda s: s.is_company)
        partners |= self.res_users_ids.mapped("partner_id").filtered(
            lambda s: s.is_company
        )
        return partners.filtered(lambda s: s.email)
