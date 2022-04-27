# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mozaik Petition",
    "summary": """
        This addon encodes petitions:
        - a list of sponsors
        - a list of questions to ask to signatories
        - a list of signatories as well as their answers to questions
        - milestones
        """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "depends": [
        # OCA/partner-contact
        "partner_firstname",
        # Odoo
        "contacts",
        "mail",
        "mozaik_thesaurus",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/petition_type.xml",
        "views/petition_registration.xml",
        "views/petition_petition.xml",
        "views/petition_question.xml",
        "views/petition_milestone.xml",
        "views/petition_menus.xml",
        "data/ir_config_parameter.xml",
        "data/petition_type_data.xml",
        "data/petition_question_data.xml",
        "data/petition_petition_data.xml",
    ],
    "demo": [
        "data/email_template_demo.xml",
    ],
    "external_dependencies": {"python": ["freezegun"]},
}
