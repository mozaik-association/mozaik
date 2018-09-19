# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, fields, models, _


class PostalMailLog(models.Model):
    _name = "postal.mail.log"
    _inherit = ['mozaik.abstract.model']
    _description = 'Postal Mail Log'
    _order = 'sent_date desc, partner_id'
    _unicity_keys = 'N/A'

    name = fields.Char(
        track_visibility='onchange',
    )
    sent_date = fields.Date(
        required=True,
        track_visibility='onchange',
        default=fields.Date.today,
    )
    postal_mail_id = fields.Many2one(
        comodel_name="postal.mail",
        string="Postal mailing",
        readonly=True,
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name="postal.coordinate",
        string="Postal coordinate",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )
    partner_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Partner internal instance",
        index=True,
        readonly=True,
        related="partner_id.int_instance_id",
        store=True,
    )

    @api.multi
    def name_get(self):
        """
        Keep existing display name but add the sent_date
        :return: list of tuple: (int, str)
        """
        result = super().name_get()
        new_result = []
        for target_id, __ in result:
            record = self.browse(target_id)
            name = record.name or record.postal_mail_id.name
            new_result.append((target_id, name))
        return new_result

    @api.multi
    def copy(self, default=None):
        """
        Do not copy if postal_mail_id is set.
        :param default: None or dict
        :return: self recordset
        """
        self.ensure_one()
        default = default or {}
        if self.postal_mail_id:
            raise exceptions.ValidationError(
                _('A postal mail log cannot be copied when linked to a '
                  'postal mailing!'))
        return super().copy(default=default)

    @api.onchange("postal_coordinate_id", "partner_id")
    def _onchange_postal_coordinate_id(self):
        """
        Set the partner_id to the id of the partner
        of the selected postal coordinate.
        :return: dict
        """
        domain = []
        if self.postal_coordinate_id:
            self.partner_id = self.postal_coordinate_id.partner_id
        elif self.partner_id:
            domain = [('partner_id', '=', self.partner_id.id)]
        values = {
            'domain': {
                'postal_coordinate_id': domain,
            }
        }
        return values
