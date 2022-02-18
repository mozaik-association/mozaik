# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.event_rest_api.pydantic_models.event_registration_request import (
    EventRegistrationRequest,
)


class EventService(Component):
    _inherit = "event.rest.service"

    def _get_search_domain(self, filters):
        domain = super()._get_search_domain(filters)
        if filters.website_domain_ids:
            domain.append(("website_domain_ids", "in", filters.website_domain_ids))
        if filters.interest_ids:
            domain.append(("interest_ids", "in", filters.interest_ids))
        return domain

    def _prepare_event_registration_values(
        self, event, event_registration_request: EventRegistrationRequest
    ) -> dict:
        """
        Adding a check: if registered_partner_id is not given,
        then firstname, lastname and email are mandatory.
        """
        if not event_registration_request.registered_partner_id and not all(
            [
                event_registration_request.lastname,
                event_registration_request.firstname,
                event_registration_request.email,
            ]
        ):
            raise ValidationError(
                _(
                    "If registered_partner_id is not given, "
                    "firstname, lastname and email are mandatory"
                )
            )

        res = super()._prepare_event_registration_values(
            event, event_registration_request
        )
        answers = []
        for answer in event_registration_request.answers:
            answers.append(
                (
                    0,
                    0,
                    {
                        "question_id": answer.question_id,
                        "value_answer_id": answer.value_answer_id,
                        "value_text_box": answer.value_text_box,
                        "value_tickbox": answer.value_tickbox,
                    },
                )
            )
        res["registration_answer_ids"] = answers
        res["associated_partner_id"] = (
            event_registration_request.registered_partner_id or False
        )
        return res
