# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, fields, models, _, SUPERUSER_ID
from odoo.osv import expression


class PostalMail(models.Model):
    _name = "postal.mail"
    _inherit = ['mozaik.abstract.model']
    _description = 'Postal Mailing'
    _order = 'sent_date desc, name'

    _inactive_cascade = True
    _unicity_keys = 'sent_date, name'

    name = fields.Char(
        required=True,
        track_visibility='onchange',
    )
    sent_date = fields.Date(
        required=True,
        track_visibility='onchange',
        default=fields.Date.today,
        copy=False,
    )
    postal_mail_log_count = fields.Integer(
        string="Log count",
        compute="_compute_postal_mail_log_count",
        store=True,
    )
    postal_mail_log_ids = fields.One2many(
        comodel_name="postal.mail.log",
        inverse_name="postal_mail_id",
        string="Logs",
    )

    @api.multi
    @api.depends('postal_mail_log_count')
    def _compute_postal_mail_log_count(self):
        """
        Compute the number of postal_mail_log_ids related
        :return:
        """
        for record in self:
            record.postal_mail_log_count = len(record.postal_mail_log_ids)

    @api.multi
    def copy(self, default=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        :param default: None or dict
        :return: self recordset
        """
        self.ensure_one()
        default = default or {}
        default.update({
            'name': _('%s (copy)') % self.name,
        })
        return super(PostalMail, self).copy(default=default)

    @api.multi
    def name_get(self):
        """
        Keep existing display name but add the sent_date
        :return: list of tuple: (int, str)
        """
        result = super(PostalMail, self).name_get()
        new_result = []
        for postal_id, display_name in result:
            postal_mail = self.browse(postal_id)
            name = "%s (%s)" % (display_name, postal_mail.sent_date)
            new_result.append((postal_id, name))
        return new_result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """

        :param name:
        :param args:
        :param operator:
        :param limit:
        :return:
        """
        args = args or []
        domain = [
            '|',
            ('name', operator, name),
            ('sent_date', operator, name),
        ]
        if args:
            args = expression.AND([domain, args or []])
        return super(PostalMail, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
