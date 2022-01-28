# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, exceptions

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import Component

from ..pydantic_models.petition_registration import PetitionRegistration
from ..pydantic_models.petition_registration_info import PetitionRegistrationInfo


class PetitionRegistrationService(Component):
    _inherit = "base.petition.rest.service"
    _name = "petition.registration.rest.service"
    _usage = "petition.registration"
    _expose_model = "petition.registration"
    _description = __doc__

    @restapi.method(
        routes=[(["/register_answer"], "POST")],
        input_param=PydanticModel(PetitionRegistration),
        output_param=PydanticModel(PetitionRegistrationInfo),
        auth="public_or_default",
    )
    def register_answer(
        self, petition_registration: PetitionRegistration
    ) -> PetitionRegistrationInfo:
        # Control variable to check if we can continue treatement of the
        # request
        answer_validated = True
        # Checking every answer before register it
        for answer in petition_registration.list_answer:
            question = self.env["petition.question"].search(
                [("id", "=", answer.question_id)]
            )
            if question:
                if question.is_mandatory:
                    if question.question_type == "simple_choice":
                        if answer.value_answer_id is None:
                            answer_validated = False
                            raise exceptions.ValidationError(
                                _("Question with id: '%s' , is Mandatory" % question.id)
                            )
                    elif question.question_type == "text_box":
                        if answer.value_text_box is None:
                            answer_validated = False
                            raise exceptions.ValidationError(
                                _("Question with id: '%s' , is Mandatory" % question.id)
                            )
                    elif question.question_type == "tickbox":
                        if answer.value_tickbox is None:
                            answer_validated = False
                            raise exceptions.ValidationError(
                                _("Question with id: '%s' , is Mandatory" % question.id)
                            )
            else:
                answer_validated = False

        if answer_validated:
            # if all answer validated creating the petition registration
            vals = petition_registration.dict()
            del vals["list_answer"]
            res = self.env["petition.registration"].create(vals)
            # Store the answer in a variable to create all answer in once
            vals_answer = {}
            for answer in petition_registration.list_answer:
                question = self.env["petition.question"].search(
                    [("id", "=", answer.question_id)]
                )
                vals_answer[question.id] = {}
                vals_answer[question.id]["question_id"] = answer.question_id

                vals_answer[question.id]["petition_id"] = [
                    petition_registration.petition_id
                ]
                # store registration reference in answer
                vals_answer[question.id]["registration_id"] = res.id
                # Store value of answer
                if question.question_type == "simple_choice":
                    vals_answer[question.id]["value_answer_id"] = answer.value_answer_id
                elif question.question_type == "text_box":
                    vals_answer[question.id]["value_text_box"] = answer.value_text_box
                elif question.question_type == "tickbox":
                    vals_answer[question.id]["value_tickbox"] = answer.value_tickbox
            # Create a list of reference to the question registered
            answer_list_id = []
            for answer in vals_answer:
                registered_answer = self.env["petition.registration.answer"].create(
                    vals_answer[answer]
                )
                answer_list_id.append(registered_answer.id)
            # Updating registration with answers
            vals_answer = {"registration_answer_ids": (4, answer_list_id)}
            res.update(vals)

            return PetitionRegistrationInfo.from_orm(res)
        else:
            raise exceptions.ValidationError(
                _("Question Mandatory not answered")
            )
