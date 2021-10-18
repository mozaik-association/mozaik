# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Mailing Distribution List',
    'summary': """
        Make the bridge between distribution list and mass mailing""",
    'version': "14.0.1.0.0",
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'category': 'Marketing',
    'depends': [
        'distribution_list',
        'mass_mailing',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/mail_alias.xml',
        'views/mass_mailing.xml',
        'views/distribution_list.xml',
        'wizards/merge_distribution_list.xml',
    ],
    "installable": True,
}
