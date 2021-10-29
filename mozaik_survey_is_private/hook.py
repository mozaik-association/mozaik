# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo


def pre_init_hook(cr):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    xml_ids = [
        "survey.survey_survey_rule_survey_user_read",
        "survey.survey_question_rule_survey_user_read",
        "survey.survey_question_answer_rule_survey_user_read",
        "survey.survey_user_input_rule_survey_user_read",
        "survey.survey_user_input_line_rule_survey_user_read",
    ]

    for xml_id in xml_ids:
        ir_rule = env.ref(xml_id)
        if ir_rule.active:
            ir_rule.active = False
