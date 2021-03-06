# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mail Job Priority',
    'description': """
        Compute a priority for sending jobs depending on a parameter
        and on the size of the recipients list""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'mail',
        'mail_connector_queue',
        # following depend is to be sure
        # to compute priority before delegating mails sending to the connector
        # because they overlaod together the same method
        'asynchronous_batch_mailings',
        'distribution_list',
    ],
    'data': [
    ],
    'demo': [
    ],
}
