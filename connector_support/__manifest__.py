# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Connector Support',
    'description': """
        Add the security group Connector Support.
        Only its members receive notifications when a job fails.
        Only this group view Connector Menu""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': [
        'connector',
    ],
    'data': [
        'security/connector_support_security.xml',
        'views/queue_job.xml',
    ],
    'demo': [
    ],
    "installable": False,
}
