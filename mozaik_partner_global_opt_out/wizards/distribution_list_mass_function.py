# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DistributionListMassFunction(models.TransientModel):

    _inherit = "distribution.list.mass.function"

    include_opt_out_contacts = fields.Boolean(
        default=False,
        string="Include opt-out contacts",
        help="If True, include contacts whose email is blacklisted.",
    )

    def _mass_email_coordinate(self, fct, main_domain):
        mains, alternatives = super()._mass_email_coordinate(fct, main_domain)
        if not self.include_opt_out_contacts:
            # Remove blacklisted contacts
            mains = self._remove_opt_out_contacts(mains)
            alternatives = self._remove_opt_out_contacts(alternatives)
        return mains, alternatives

    def _remove_opt_out_contacts(self, contacts):
        """
        If model is res.partner : remove contacts with global_opt_out.
        If model is virtual.target : remove records for which
        the associated contact has global opt-out
        """
        if "partner_id" in contacts._fields:
            return contacts.filtered(lambda vt: not vt.partner_id.global_opt_out)
        return contacts.filtered(lambda p: not p.global_opt_out)

    def _create_mail_composer(self):
        res = super()._create_mail_composer()
        res.write({"include_opt_out_contacts": self.include_opt_out_contacts})
        return res

    def _update_mass_mailing(self, mail_composer, mass_mailing):
        super()._update_mass_mailing(mail_composer, mass_mailing)
        if mail_composer:
            mass_mailing.write(
                {"include_opt_out_contacts": mail_composer.include_opt_out_contacts}
            )
