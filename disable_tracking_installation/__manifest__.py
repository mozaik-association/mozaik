# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Disable tracking installation',
    'summary': """
        Module to disable tracking during installation, migration and tests""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': [
        'base',
        'mail',
    ],
    "installable": False,
}
