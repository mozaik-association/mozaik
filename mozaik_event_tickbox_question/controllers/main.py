# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.website_event_questions.controllers.main import WebsiteEvent


class WebsiteEventQuestionTickbox(WebsiteEvent):
    def _process_attendees_form(self, event, form_details):
        registrations = super()._process_attendees_form(event, form_details)

        general_answer_ids = []
        for key, value in form_details.items():
            if "question_answer" in key:
                dummy, registration_index, question_id = key.split("-")
                question_sudo = request.env["event.question"].browse(int(question_id))
                answer_values = None

                if question_sudo.question_type == "tickbox":
                    answer_values = {
                        "question_id": int(question_id),
                        "value_tickbox": value == "on",
                    }

                if answer_values and not int(registration_index):
                    general_answer_ids.append((0, 0, answer_values))
                elif answer_values:
                    registrations[int(registration_index) - 1][
                        "registration_answer_ids"
                    ].append((0, 0, answer_values))

        for registration in registrations:
            registration["registration_answer_ids"].extend(general_answer_ids)

        return registrations
