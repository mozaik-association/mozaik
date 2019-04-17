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
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'wizards/abstract_copy_mandate_wizard.xml',
        'wizards/abstract_update_mandate_end_date_wizard.xml',
        'wizards/update_ext_mandate_end_date_wizard.xml',
        'wizards/update_int_mandate_end_date_wizard.xml',
        'wizards/update_sta_mandate_end_date_wizard.xml',
        'wizards/copy_ext_mandate_wizard.xml',
        'wizards/copy_int_mandate_wizard.xml',
        'wizards/copy_sta_mandate_wizard.xml',
        'views/int_instance.xml',
        'views/ext_assembly_category.xml',
        'views/int_assembly_category.xml',
        'views/sta_assembly_category.xml',
        'wizards/allow_incompatible_mandate_wizard.xml',
        'views/generic_mandate.xml',
        'views/abstract_mandate.xml',
        'views/sta_mandate.xml',
        'views/int_mandate.xml',
        'views/ext_mandate.xml',
        'views/res_partner.xml',
        'views/legislature.xml',
        'views/mandate_category.xml',
        'data/ir_cron_mandate.xml',
    ],
    'qweb': [
    ],
    'demo': [
        'demo/mandate_category.xml',
        'demo/legislature.xml',
        'demo/ext_mandate.xml',
        'demo/int_mandate.xml',
        'demo/sta_mandate.xml',
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
}
