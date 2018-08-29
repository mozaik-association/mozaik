# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: All Modules Loader',
    'summary': """
        Loads all Mozaik modules""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'disable_user_welcome_message',
        'partner_usual_firstname',
        'mozaik_abstract_model',
        'mozaik_structure',
        'mozaik_duplicate',
        'mozaik_coordinate',
        'mozaik_address',
        'mozaik_address_local_street',
        'mozaik_email',
        'mozaik_phone',
        'mozaik_partner_unauthorized',
        'mozaik_partner_fields',
        'mozaik_involvement',
        'mozaik_person',
    ],
    'data': [
        'views/mail_followers.xml',
    ],
    'installable': True,
}
