# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mail Job Priority',
    'description': """
        Compute a priority for sending jobs depending on a parameter
        and on the size of the recipients list""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://github.com/OCA/mozaik',
    'depends': [
        'mail',
        'mail_queue_job',
    ],
    "installable": False,
}
