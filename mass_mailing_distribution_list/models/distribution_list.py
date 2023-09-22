# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import re

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)
MATCH_EMAIL = re.compile("<(.*)>", re.IGNORECASE)


class DistributionList(models.Model):
    _inherit = "distribution.list"

    newsletter = fields.Boolean(default=False)
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
                and distribution_list.partner_path
                not in distribution_list.dst_model_id.field_id.mapped("name")
            ):
                raise exceptions.ValidationError(
                    _(
                        "Partner Path is not valid: this field doesn't exist on model '%s'"
                        % distribution_list.dst_model_id.name
                    )
                )

    def _get_opt_res_ids(self, domain):
        """
        Get destination model opt/in opt/out records
        :param domain: list
        :return: dst model recordset
        """
        self.ensure_one()
        opt_ids = self.env[self.dst_model_id.model].search(domain)
        return opt_ids

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
                vals.update({opt_field: opt_val})
            res = self.write(vals)
            return res
        return False
