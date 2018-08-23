# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mass Mailing Distribution List',
    'version': '11.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'distribution_list',
        'mass_mailing',
    ],
    'description': """
Mass Mailing Distribution List
==============================

This module make a link between distribution list and mass mailing.

It allows:
* to declare a distribution list as a newsletter to also define
  static lists of partners (opt In/Out)
* to unsubscribe partner (i.e. add it to the opt Out list) through
  the unsubscribe link added to the mailing
* to receive an external mail and forward it to all recipients filtered by
  the distribution list
""",
    'data': [
        'data/ir_config_parameter.xml',
        'views/mass_mailing.xml',
        'views/distribution_list.xml',
        'wizards/merge_distribution_list.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
