# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    email_bounced_date = fields.Datetime("Last failure date")
    first_email_bounced_date = fields.Datetime(
        "First failure date",
    )
    can_edit_bounce_params = fields.Boolean(compute="_compute_can_edit_bounce_params")

    def _compute_can_edit_bounce_params(self):
        self.write(
            {
                "can_edit_bounce_params": self.env.user.has_group(
                    "mozaik_mass_mailing_bounce_counter.group_mass_mailing_bounce_counter"
                )
            }
        )

    def write(self, values):
        if values.get("email_bounced", 1) == 0:
            values.update(
                {
                    "email_bounced_date": False,
                    "first_email_bounced_date": False,
                }
            )
        return super().write(values)

    @api.model
    def _update_bounce_counter(self, last_execution):
        """
        Look at mass mailings sent since the last execution.
        Update bounce counters:
        if bounced email: increment the counter, write failure date
        if no bounced email and counter > 0 : counter set back to 0.
        """
        mailing_traces = (
            self.env["mailing.trace"]
            .search(
                [("state_update", ">", last_execution), ("model", "=", "res.partner")]
            )
            .filtered(lambda mt: mt.mass_mailing_id)
        )
        mailing_traces_sent = mailing_traces.filtered(
            lambda mt: mt.sent
            and mt.sent > last_execution
            and (not mt.bounced or mt.sent > mt.bounced)
        )
        mailing_traces_bounced = mailing_traces.filtered(
            lambda mt: mt.bounced
            and mt.bounced > last_execution
            and (not mt.sent or mt.sent < mt.bounced)
        )

        # For each bounced mailing trace, update email_bounced_counter
        for mtb in mailing_traces_bounced:
            if mtb.model != "res.partner":
                continue
            partner = self.env["res.partner"].browse(mtb.res_id)
            vals = {
                "email_bounced": partner.email_bounced + 1,
            }
            if (
                not partner.first_email_bounced_date
                or mtb.bounced < partner.first_email_bounced_date
            ):
                vals["first_email_bounced_date"] = mtb.bounced
            if (
                not partner.email_bounced_date
                or mtb.bounced > partner.email_bounced_date
            ):
                vals["email_bounced_date"] = mtb.bounced
            partner.write(vals)

        # For each sent mailing trace, set the counter back to 0, if no failure this execution
        for mts in mailing_traces_sent:
            if mts.model != "res.partner":
                continue
            partner = self.env["res.partner"].browse(mts.res_id)
            if (
                partner.email_bounced > 0
                and (
                    partner.email_bounced_date
                    and partner.email_bounced_date < last_execution
                )
                or not partner.email_bounced_date
            ):
                partner.write(
                    {
                        "email_bounced": 0,
                        "email_bounced_date": False,
                        "first_email_bounced_date": False,
                    }
                )
