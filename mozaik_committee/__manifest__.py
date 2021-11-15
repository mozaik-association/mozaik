# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik Committee',
    'description': """
        committee""",
    'version': "14.0.1.0.0",
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': ["mozaik_mandate", "statechart"],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/abstract_candidature.xml',
        'views/abstract_mandate.xml',
        'views/abstract_selection_committee.xml',
        'views/ext_candidature.xml',
        'views/int_candidature.xml',
        'views/sta_candidature.xml',
        'views/sta_mandate.xml',
        'views/mandate_category.xml',
        'views/ext_assembly.xml',
        'views/int_assembly.xml',
        'views/sta_assembly.xml',
        'views/int_instance.xml',
        'views/res_partner.xml',
        'views/ext_selection_committee.xml',
        'views/int_selection_committee.xml',
        'views/sta_selection_committee.xml',
        'views/electoral_district.xml',
        'views/legislature.xml',
        'wizards/electoral_results_wizard.xml',
        'data/ir_config_parameter_data.xml',
        'data/ir_cron_mandate.xml',
    ],
    'demo': [
        'demo/selection_committee_demo.xml',
        'demo/candidature_demo.xml',
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
