# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

STATE_TYPE = [
    ("nofollowup", "Without follow-up"),
    ("followup", "To follow"),
    ("late", "Late follow-up"),
    ("done", "Followed"),
]


class PartnerInvolvement(models.Model):
    _name = "partner.involvement"
    _inherit = ["partner.involvement", "mail.activity.mixin"]

    _track = {
        "state": {
            "mozaik_involvement_followup"
            ".partner_involvement_to_follow_mms": (
                lambda self, cr, uid, brec, c=None: brec.state == "followup"
            ),
            "mozaik_involvement_followup"
            ".partner_involvement_late_mms": (
                lambda self, cr, uid, brec, c=None: brec.state == "late"
            ),
        },
    }

    state = fields.Selection(
        selection=STATE_TYPE,
        index=True,
        tracking=True,
        copy=False,
        default="nofollowup",
    )

    deadline = fields.Date(
        index=True, copy=False, store=True, compute="_compute_deadline"
    )

    from_date = fields.Date(copy=False)  # only to trigger a recompute

    @api.depends("involvement_category_id", "from_date")
    def _compute_deadline(self):
        for involvement in self:
            if involvement.involvement_category_id.nb_deadline_days:
                deadline = (
                    date.today()
                    + timedelta(
                        days=involvement.involvement_category_id.nb_deadline_days
                    )
                ).strftime(DATE_FORMAT)
                involvement.deadline = deadline
            else:
                involvement.deadline = False

    @api.model_create_single
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        """
        Launch followup if any
        """
        res = super(PartnerInvolvement, self).create(vals)
        if res.deadline and not res.env.context.get("disable_followup"):
            cat = res.involvement_category_id.sudo()
            fol_ids = []
            if cat.mandate_category_id:
                fol_representatives = (
                    cat.mandate_category_id._get_active_representative(
                        res.partner_id.int_instance_id.id, True
                    )
                )
                fol_ids += fol_representatives
                if fol_representatives:
                    activity_vals = self._schedule_activity_reminder(
                        fol_representatives[0], res
                    )
                    res["activity_ids"] = [(0, 0, activity_vals)]
            fol_ids += cat.message_follower_ids.ids
            res.message_subscribe(fol_ids)
            res.state = "followup"
        return res

    @api.model
    def _schedule_activity_reminder(self, user_partner_id, involvement):
        """
        Prepare values for scheduling an activity for the given user.
        user_partner_id is the id of the partner associated to the concerned user.
        """
        note = "<p> Partner: %s </p> <p> Subject: %s </p>" % (
            involvement.partner_id.name,
            involvement.involvement_category_id.name,
        )
        vals = {
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": "Involvement to follow",
            "note": note,
            "date_deadline": involvement.deadline,
            "automated": True,
            "res_model_id": self.env["ir.model"]
            .search([("model", "=", "partner.involvement")])
            .id,
            "res_id": involvement.id,
        }
        if user_partner_id:
            user_ids = self.env["res.partner"].browse(user_partner_id).user_ids
            if user_ids:
                vals["user_id"] = user_ids[0].id
        return vals

    @api.model
    def _set_state_as_late(self):
        """
        Called by cron
        Change state of all 'followup' involvements with a passed deadline
        Effect is a tracking notification to subscribed followers to the
        corresponding subtype
        """
        today = fields.Date.today()
        invs = self.search(
            [
                ("deadline", "!=", False),
                ("deadline", "<=", today),
                ("state", "=", "followup"),
            ]
        )
        invs.write({"state": "late"})
        return True

    @api.model
    def read_followers_data(self, follower_ids):
        """
        Disable security for this method but recompute is_uid properties
        """
        result = super(PartnerInvolvement, self.sudo()).read_followers_data(
            follower_ids
        )
        is_editable = self.user_has_groups("mozaik_base.mozaik_res_groups_configurator")
        uid = self.env.user.partner_id.id
        for res in result:
            res[2]["is_editable"] = is_editable
            res[2]["is_uid"] = uid == res[0]
        return result
