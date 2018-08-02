# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Base',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base',
        'document',
        'contacts',
        # from https://github.com/OCA/server-tools
        # 'auth_admin_passkey',  # Not exists in v11.0?
    ],
    'description': """
MOZAIK Base
===========
* define Mozaik menus skeleton
""",
    'data': [
        'data/ir_config_parameter.xml',
        'data/ir_ui_menu.xml',
        'data/mail_message_subtype.xml',
        'data/res_lang.xml',
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'views/assets_backend.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
