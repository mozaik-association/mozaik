# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import os

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):

    _inherit = "event.registration"

    @api.model
    def _get_random_token(self):
        """Generate a 20 char long pseudo-random string of digits for barcode
        generation.
        """
        return str(int.from_bytes(os.urandom(8), "little"))

    barcode = fields.Char(
        default=_get_random_token, readonly=True, copy=False, index=True
    )
    is_voting_domain_required = fields.Boolean(
        related="event_id.is_voting_domain_required"
    )
    can_vote = fields.Boolean(
        string="Can vote",
        compute="_compute_can_vote",
        store=True,
        help="If voting domain required boolean is ticked on the event, "
        "this boolean shows if the partner can vote or not. "
        "NB: If the voting domain is not activated on the event, "
        "all registrations will have can_vote=False, "
        "this being to avoid long computations.",
    )

    @api.depends(
        "associated_partner_id",
        "event_id.voting_domain",
        "event_id.is_voting_domain_required",
    )
    def _compute_can_vote(self):
        """
        This computation is quite long because the only way is to apply the
        voting domain on the virtual.partner.membership model, then retrieving
        the related partners.
        The is_voting_domain_required inactivates this functionality when
        it's not needed on the event.
        :return:
        """
        reg_voting_domain_required = self.filtered("is_voting_domain_required")
        reg_no_voting_domain = self - reg_voting_domain_required
        reg_no_voting_domain.can_vote = False
        # Compute voting partners once
        voting_partners_dict = {}
        for event in list(set(reg_voting_domain_required.mapped("event_id"))):
            voting_partners_dict[event.id] = event._get_voting_partners()
        for record in reg_voting_domain_required:
            if not record.associated_partner_id:
                record.can_vote = False
            else:
                record.can_vote = (
                    record.associated_partner_id.id
                    in voting_partners_dict[record.event_id.id]
                )

    _sql_constraints = [
        ("barcode_event_uniq", "unique(barcode)", "Barcode should be unique")
    ]

    def _init_column(self, column_name):
        """When installing the module, odoo will generate the same barcode
        for all existing event.registration records.
        But we want a different barcode for each registration.
        """
        if column_name == "barcode":
            _logger.info(
                "Setting unique barcode on all existing event.registration records"
            )
            self.env.cr.execute(
                "SELECT id FROM event_registration WHERE barcode IS NULL"
            )
            registration_ids = self.env.cr.dictfetchall()
            query_list = [
                {"id": reg["id"], "barcode": self._get_random_token()}
                for reg in registration_ids
            ]
            query = (
                "UPDATE event_registration SET barcode = %(barcode)s WHERE id = %(id)s;"
            )
            for elem in query_list:
                self.env.cr.execute(query, elem)
        else:
            super(EventRegistration, self)._init_column(column_name)
