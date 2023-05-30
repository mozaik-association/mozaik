# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    last_changes = fields.Text(copy=False)
    last_changes_sequence = fields.Integer(
        string="Change Sequence", index=True, copy=False, default=999
    )

    @api.model
    def create(self, vals):
        partner = self.env["res.partner"].browse(vals.get("partner_id"))
        changes = partner._before_new_membership_created(vals)
        res = super().create(vals)
        partner._after_new_membership_created(changes)
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("paid"):
            sequence, change = self.env["res.partner"]._get_state_changes_dict()[
                "renewal"
            ]
            self.partner_id._add_change_to_partner(change, sequence)
        return res

    def _add_change(self, change, sequence):
        for ml in self:
            if not change:
                continue
            changes = [ml.last_changes] if ml.last_changes else []
            changes += ["%03d: %s" % (sequence, change)]
            vals = {
                "last_changes": "\n".join(changes),
                "last_changes_sequence": min(sequence, ml.last_changes_sequence),
            }
            ml.write(vals)
            body = "<div> &nbsp; &nbsp; &bull; <b>{}</b>: {}".format(
                _("Last Change"),
                change,
            )
            ml.message_post(body=body)

    @api.model
    def get_last_changes(self, int_instance_id=False):
        """
        Return memberhsip lines with changes to add into the report
        :int_instance_id: if an int instance is specified, limit the MLs to this instance
        """
        dom = [("last_changes", "!=", False)]
        if int_instance_id:
            dom += [("int_instance_id", "=", int_instance_id.id)]
        order = "int_instance_id, last_changes_sequence, partner_id, write_date desc"
        res = self.with_context(active_test=False).search(dom, order=order)
        return res

    def reset_last_changes(self):
        self.write({"last_changes": False, "last_changes_sequence": 999})

    @api.model
    def send_last_changes(self):
        lines_with_changes = self.get_last_changes()
        instances = lines_with_changes.mapped("int_instance_id")
        secretariat_ids = self.env["int.assembly"]
        for instance in instances:
            secretariat_ids |= instance._get_secretariat()
        secretariat_ids.send_last_changes()
        lines_with_changes.reset_last_changes()

    def get_partner_phones(self):
        """
        This method is not used but is available for the user
        who needs it in the mail template.
        """
        self.ensure_one()
        partner = self.partner_id
        phones = []
        if partner.phone:
            phones.append(partner.phone)
        if partner.mobile:
            phones.append(partner.mobile)
        return phones

    def get_partner_state_and_voluntaries(self):
        """
        This method is not used but is available for the user
        who needs it in the mail template.
        """
        self.ensure_one()
        states = [self.state_id.name]
        if self.state_id.code in ("member_candidate", "member_committee", "member"):
            partner = self.partner_id
            states += [
                _("[%s] Local voluntary") % (partner.local_voluntary and "X" or " "),
                _("[%s] Regional voluntary")
                % (partner.regional_voluntary and "X" or " "),
                _("[%s] National voluntary")
                % (partner.national_voluntary and "X" or " "),
            ]
        return states
