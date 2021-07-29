# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mozaik Mandate Female Label',
    'description': """
        Add a female name on mandate category""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'mail',
        'partner_contact_gender',
        'mozaik_mandate',
    ],
    'data': [
        'views/abstract_mandate.xml',
        'views/mandate_category.xml',
    ],
    'demo': [
        'demo/mandate_category.xml',
    ],
    'pre_init_hook': '_copy_name_to_female_name',
    "installable": False,
}
