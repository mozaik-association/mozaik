# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.event_rest_api.pydantic_models.event_registration_request import (
    EventRegistrationRequest,
)


class EventService(Component):
    _inherit = "event.rest.service"

    def _get_search_domain(self, filters):
        domain = super()._get_search_domain(filters)
        if filters.is_private:
            domain.append(("is_private", "=", filters.is_private))
        if filters.website_domain_ids:
            domain.append(("website_domain_ids", "in", filters.website_domain_ids))
        if filters.interest_ids:
            domain.append(("interest_ids", "in", filters.interest_ids))
        return domain

    def _prepare_event_registration_values(
        self, event, event_registration_request: EventRegistrationRequest
    ) -> dict:
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
        return res
