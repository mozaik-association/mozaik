# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Communication',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mass_mailing_distribution_list',
        'mozaik_person',
        'mozaik_structure',
        'mozaik_membership',
        'mozaik_retrocession',
        # from https://github.com/OCA/social
        'email_template_configurator',
    ],
    'description': """
MOZAIK Communication
====================
* New Menus:
** Communication/Persons
** Communication/Mailing
** Communication/Postal Mailing
** Communication/Configuration
* Customization of the Distribution List Module
""",
    'images': [
        'static/src/img/icon-mass.png',
    ],
    'data': [
        'security/mail_mass_mailing_group.xml',
        'security/ir.model.access.csv',
        'security/communication_security.xml',
        'wizard/distribution_list_mass_function_view.xml',
        'wizard/add_registrations_view.xml',
        'wizard/distribution_list_add_filter_view.xml',
        'wizard/export_csv_view.xml',
        'distribution_list_view.xml',
        'postal_mail_view.xml',
        'res_partner_view.xml',
        'communication_view.xml',
        'mass_mailing_view.xml',
        'email_template_view.xml',
        'event_view.xml',
        'membership_request_view.xml',
        'views/mail_mail_statistics_view.xml',
        'views/virtual_models_view.xml',
        'views/email_template_view.xml',
        'views/mass_mailing_report.xml',
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
