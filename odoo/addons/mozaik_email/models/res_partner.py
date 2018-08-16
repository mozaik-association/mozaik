# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.fields import first


class ResPartner(models.Model):
    _inherit = "res.partner"

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    email_coordinate_ids = fields.One2many(
        'email.coordinate',
        'partner_id',
        'Email coordinates',
        domain=[('active', '=', True)],
        copy=False,
    )
    email_coordinate_inactive_ids = fields.One2many(
        'email.coordinate',
        'partner_id',
        'Email coordinates',
        domain=[('active', '=', False)],
        copy=False,
    )
    # email_coordinate_id cannot be store=True for security issue: if the main
    # email is VIP, will be display for non vip reader if store=True
    email_coordinate_id = fields.Many2one(
        'email.coordinate',
        "Email",
        compute="_compute_email_coordinate_id",
    )
    email = fields.Char(
        compute="_compute_email_coordinate_id",
        index=True,
        store=True,
    )

    @api.multi
    @api.depends(
        'email_coordinate_ids',
        'email_coordinate_ids.is_main',
        'email_coordinate_ids.vip',
        'email_coordinate_ids.active',
        'email_coordinate_ids.email',
    )
    def _compute_email_coordinate_id(self):
        """
        Compute function to fill the email_coordinate_id and email fields.
        This email_coordinate_id should be filled with the main email address
        of the partner (using the is_main field on active email.coordinate).
        The email field should be the email found in the email_coordinate_id
        """
        for record in self:
            coordinate = self.env['email.coordinate'].browse()
            if record.active:
                coordinate = first(record.sudo().email_coordinate_ids.filtered(
                    lambda e: e.is_main).with_prefetch(self._prefetch))
            vip_group = 'mozaik_coordinate.res_groups_coordinate_vip_reader'
            if not coordinate.vip or self.user_has_groups(vip_group):
                record.email_coordinate_id = coordinate
            record.email = 'VIP' if coordinate.vip else coordinate.email
