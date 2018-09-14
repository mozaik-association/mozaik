# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK virtual assembly instance',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_communication',
        'mozaik_membership',
        'mozaik_thesaurus',
    ],
    'data': [
        'views/virtual_assembly_instance.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': True,
    'installable': True,
}
