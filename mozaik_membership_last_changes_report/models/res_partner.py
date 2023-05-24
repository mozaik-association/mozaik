# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

UNKNOWN_STAGE_SEQ = 299


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _get_state_changes_dict(self):
        """
        Return a dict whose
        * Keys are significant changes: state changes, instance changes, renewals, ...
        * Values are tuples of length 2: a code, and a char sentence,
        giving more details on the change
        """
        party_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("party_name", default=_("your organization"))
        )
        return {
            "renewal": (200, _("The person has renewed its subscription")),
            "member": (210, _("The person becomes a member in full")),
            "former_member": (
                300,
                _(
                    "The person did not renew its subscription "
                    "or its status has been reinitialized"
                ),
            ),
            "former_member_committee": (
                230,
                _(
                    "The person has renewed its "
                    "subscription. \nWithout opposite "
                    "opinion of the instance the person "
                    "will become member in one month"
                ),
            ),
            "break_former_member": (
                400,
                _("The person is no longer member of {party_name}").format(
                    party_name=party_name
                ),
            ),
            "expulsion_former_member": (
                410,
                _("The person is no longer member of {party_name}").format(
                    party_name=party_name
                ),
            ),
            "inappropriate_former_member": (
                420,
                _("The person is no longer member of {party_name}").format(
                    party_name=party_name
                ),
            ),
            "resignation_former_member": (
                430,
                _("The person is no longer member of {party_name}").format(
                    party_name=party_name
                ),
            ),
            "member_committee": (
                160,
                _(
                    "Without opposite opinion of the instance the "
                    "person will become member in one month"
                ),
            ),
            "former_supporter": (310, ""),
            "supporter": (
                120,
                _(
                    "The person becomes a supporter following a proposal "
                    "of voluntary or a donation"
                ),
            ),
        }

    def _get_state_change(self, state_id, instance_id, paid):
        self.ensure_one()
        previous_state = self.membership_state_id
        previous_instance = self.int_instance_id
        was_paid = False
        # when renewing a state, it's shortly in without state status
        if self.membership_line_ids:
            last_membership = self.membership_line_ids.sorted(
                lambda s: s.date_from, True
            )[0]
            previous_state = last_membership.state_id
            previous_instance = last_membership.int_instance_id
            was_paid = last_membership.paid

        state_changes = self._get_state_changes_dict()
        if previous_state.id == state_id:
            if (
                paid
                and paid != was_paid
                and previous_state.code == "member"
                and previous_instance.id == instance_id
            ):
                seq, msg = state_changes["renewal"]
                return seq, _(msg)
            return (999, "")
        ms_obj = self.env["membership.state"]
        state = ms_obj.browse(state_id)
        change = ""
        if state.code != "supporter":
            change = _("Status has been changed: %(previous)s → %(after)s") % {
                "previous": previous_state.name,
                "after": state.name,
            }
        seq, msg = state_changes.get(state.code, (UNKNOWN_STAGE_SEQ, ""))
        change = f"{change}. {_(msg)}"
        return seq, change

    @api.model
    def _add_change_to_partner(self, change, sequence):
        """
        Find the good membership line on the partner, to write the change on it.
        """
        self.ensure_one()
        ml = self.env["membership.line"]
        if self.membership_line_ids:
            ml = self.membership_line_ids.sorted(lambda s: s.date_from, True)[0].sudo()
        ml._add_change(change, sequence)

    def _before_new_membership_created(self, membership_vals):
        """
        Compute the changes to log.
        Log the following change: 'Has left your instance' (if applicable).
        Return the changes to log on the new membership line (when created)

        :return: dict with the following params
        * instance_change: True if the partner has changed the instance, False otherwise
        * state_change: The state change (str) to log, if applicable
        * state_seq: The state sequence (int) corresponding to the change,
        if applicable; UNKNOWN_STAGE_SEQ otherwise
        These two last params are taken out of STATE_CHANGE dict
        """
        self.ensure_one()

        instance_change = False
        state_change = False
        state_seq = False

        if membership_vals.get("state_id"):
            state_seq, state_change = self._get_state_change(
                membership_vals.get("state_id"),
                membership_vals.get("int_instance_id"),
                membership_vals.get("paid"),
            )

        previous_instance = self.int_instance_id
        # when renewing a state, it's shortly in without state status
        if self.membership_line_ids:
            previous_instance = self.membership_line_ids.sorted(
                "date_from", reverse=True
            )[0].int_instance_id
        if (
            membership_vals.get("int_instance_id")
            and membership_vals.get("int_instance_id") != previous_instance.id
        ):
            change = _("Has left your instance")
            self._add_change_to_partner(change, 520)
            instance_change = True
        return {
            "instance_change": instance_change,
            "state_change": state_change,
            "state_seq": state_seq,
        }

    def _after_new_membership_created(self, changes):
        """
        self is the partner having a new membership line
        """
        self.ensure_one()
        instance_change = changes.get("instance_change", False)
        state_change = changes.get("state_change", False)
        state_seq = changes.get("state_seq", UNKNOWN_STAGE_SEQ)

        if state_seq != UNKNOWN_STAGE_SEQ and state_change:
            self._add_change_to_partner(state_change, state_seq)

        if instance_change:
            change = _(
                "Has joined your instance following its move "
                "or following its request to join it"
            )
            self._add_change_to_partner(change, 100)

    def _get_voluntary_change(
        self, local_voluntary, regional_voluntary, national_voluntary
    ):
        self.ensure_one()
        changes = []
        if local_voluntary is not None and self.local_voluntary != local_voluntary:
            changes += [
                _("Local voluntary: [%s]") % (self.local_voluntary and "X" or " ")
            ]
        if (
            regional_voluntary is not None
            and self.regional_voluntary != regional_voluntary
        ):
            changes += [
                _("Regional voluntary: [%s]") % (self.regional_voluntary and "X" or " ")
            ]
        if (
            national_voluntary is not None
            and self.national_voluntary != national_voluntary
        ):
            changes += [
                _("National voluntary: [%s]") % (self.national_voluntary and "X" or " ")
            ]
        if changes:
            changes = _("Types of voluntaries has changed, formerly it was: %s") % (
                ", ".join(changes)
            )
        return changes

    def write(self, vals):
        """
        Log some changes on partner data on the active membership line,
        so the secretariat will receive the info.
        The concerned changes are:
        * Voluntaries fields
        * Email, postal address
        * Global opt out
        """
        for partner in self.filtered("active"):
            if any(
                [
                    "local_voluntary" in vals,
                    "regional_voluntary" in vals,
                    "national_voluntary" in vals,
                ]
            ):
                change = self._get_voluntary_change(  # TODO
                    vals.get("local_voluntary"),
                    vals.get("regional_voluntary"),
                    vals.get("national_voluntary"),
                )
                if change:
                    partner._add_change_to_partner(change, 220)
            if "email" in vals and vals["email"] != partner.email:
                change = _("Thanks to note the new email")
                partner._add_change_to_partner(change, 500)
            if (
                "address_address_id" in vals
                and vals["address_address_id"] != partner.address_address_id.id
            ):
                change = _("Thanks to note the new address")
                partner._add_change_to_partner(change, 510)
            if (
                "global_opt_out" in vals
                and vals["global_opt_out"] != partner.global_opt_out
            ):
                if vals.get("global_opt_out"):
                    change = _(
                        "Please note that the person does not wish"
                        " to receive any more emails."
                    )
                else:
                    change = _("Please note that the person accept to receive emails.")
                partner._add_change_to_partner(change, 515)
        return super().write(vals)
