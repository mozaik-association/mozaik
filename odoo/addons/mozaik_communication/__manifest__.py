# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Communication',
    'summary': """
        Manage several mass communication methods""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'mass_mailing',
        'distribution_list',
        'mass_mailing_distribution_list',
        'mozaik_abstract_model',
        'mozaik_coordinate',
        'mozaik_address',
        'mozaik_email',
        'mozaik_structure',
        'mozaik_involvement',
        #'mozaik_membership',
        # from https://github.com/OCA/social
        'email_template_configurator',
    ],
    'data': [
        'security/communication_security.xml',
        'security/mail_mass_mailing_group.xml',
        'wizards/distribution_list_mass_function.xml',
        'views/distribution_list_line.xml',
        'views/distribution_list.xml',
        'views/mail_mail_statistics.xml',
        'views/mail_mass_mailing.xml',
        'views/mail_statistics_report.xml',
        'views/mail_template.xml',
        'views/res_partner.xml',
        #'views/virtual_target.xml',
        'wizards/export_csv.xml',
    ],
    'demo': [
        'demo/distribution_list.xml',
        'demo/postal_mail.xml',
    ],
    'installable': True,
}
