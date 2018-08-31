# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mail: Build Mass Mail by Queue Job',
    'summary': """
        Build mails to send by an asynchronous way using queue job.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Marketing',
    'depends': [
        'mail',
        'queue_job',
    ],
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
}
