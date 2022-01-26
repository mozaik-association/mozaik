# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DistributionListMassFunction(models.TransientModel):

    _inherit = "distribution.list.mass.function"

    def _update_mass_mailing(self, mail_composer, mass_mailing):
        super()._update_mass_mailing(mail_composer, mass_mailing)
        if mail_composer and mail_composer.template_id:
            mass_mailing.write({"mail_template_id": mail_composer.template_id.id})
