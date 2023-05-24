# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IntInstance(models.Model):

    _inherit = "int.instance"

    def get_secretariat(self):
        """
        Secretariat needs to be available in a public way for email template recipients.
        Use this method only when you cannot use the private version _get_secretariat().
        """
        return self._get_secretariat()

    def get_last_changes(self):
        """
        Returns last changes regarding partners associated to a particular instance

        This method is not used but is available for the user
        who needs it in the mail template.
        """
        self.ensure_one()
        return self.env["membership.line"].get_last_changes(self)

    @api.model
    def get_structured_last_changes(self):
        """
        Returns structured last changes in multidimensional dict
        ordered by changes

        This method is not used but is available for the user
        who needs it in the mail template.
        """
        all_last_changes = self.get_last_changes()
        structured_lc = {}
        sorted_structured_lc = []
        for partner in all_last_changes:
            partner_changes = partner.last_changes.split("\n")
            for changes in partner_changes:
                ml_changes = {}
                ml_changes[0] = changes[5:]
                ml_changes[1] = partner
                if int(changes[0:3]) not in structured_lc:
                    structured_lc[int(changes[0:3])] = []
                structured_lc[int(changes[0:3])].append(ml_changes)
            sorted_structured_lc = sorted(structured_lc.items())
        return sorted_structured_lc
