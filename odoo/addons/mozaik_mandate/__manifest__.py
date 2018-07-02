# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Mandate',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_structure',
        'mozaik_duplicate',
        'mozaik_address',
        'mozaik_email',
        'mozaik_person',
    ],
    'description': """
MOZAIK Mandate
==============
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/copy_mandate_wizard.xml',
        'wizard/import_candidatures_wizard.xml',
        'wizard/allow_incompatible_mandate_wizard.xml',
        'wizard/electoral_results_wizard.xml',
        'wizard/update_mandate_end_date_wizard.xml',
        'abstract_mandate_view.xml',
        'mandate_view.xml',
        'res_partner_view.xml',
        'structure_view.xml',
        'sta_mandate_workflow.xml',
        'int_mandate_workflow.xml',
        'ext_mandate_workflow.xml',
        'data/ir_cron_mandate.xml',
        'data/ir_config_parameter_data.xml'
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
}
