# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    phone_coordinate_ids = fields.One2many(
        'phone.coordinate',
        'partner_id',
        'Phone Coordinates',
        copy=False,
        domain=[('active', '=', True)],
    )
    phone_coordinate_inactive_ids = fields.One2many(
        'phone.coordinate',
        'partner_id',
        'Phone Coordinates',
        copy=False,
        domain=[('active', '=', False)],
    )
    fix_coordinate_id = fields.Many2one(
        "phone.coordinate",
        string='Phone',
        compute="_compute_phone_numbers",
    )
    mobile_coordinate_id = fields.Many2one(
        "phone.coordinate",
        'Mobile',
        compute='_compute_phone_numbers',
    )
    fax_coordinate_id = fields.Many2one(
        "phone.coordinate",
        'Fax',
        compute='_compute_phone_numbers',
    )
    phone = fields.Char(
        compute="_compute_phone_numbers",
        store=True,
        index=True,
    )
    mobile = fields.Char(
        compute="_compute_phone_numbers",
        store=True,
        index=True,
    )
    fax = fields.Char(
        string='Fax',
        compute="_compute_phone_numbers",
        store=True,
        index=True,
    )

    @api.multi
    @api.depends(
        'phone_coordinate_ids',
        'phone_coordinate_ids.phone_id',
        'phone_coordinate_ids.is_main',
        'phone_coordinate_ids.vip',
        'phone_coordinate_ids.unauthorized',
        'phone_coordinate_ids.active',
        'phone_coordinate_inactive_ids.active',
        'phone_coordinate_ids.phone_id.name',
        'phone_coordinate_ids.phone_id.type',
        'phone_coordinate_ids.phone_id.also_for_fax',
    )
    def _compute_phone_numbers(self):
        """
        Compute function for these fields:
        - Phone
        - Fax
        - Mobile
        These fields are filled depending on phone_coordinate_ids
        :return:
        """
        domain = [
            ('partner_id', 'in', self.ids),
            ('is_main', '=', True),
            ('active', '=', True),
        ]
        all_phone_coordinates = self.env['phone.coordinate'].sudo().search(
            domain)
        vip = 'VIP'
        for record in self:
            # Get coordinate phone depending of the type(fix, fax, mobile)
            phone_coordinates = all_phone_coordinates.filtered(
                lambda c, p=record: c.partner_id.id == p.id)
            phone_coordinates = phone_coordinates.with_prefetch(self._prefetch)
            fix_coordinate = phone_coordinates.filtered(
                lambda c: c.coordinate_type == 'fix')
            fix_coordinate = fix_coordinate.with_prefetch(self._prefetch)
            fax_coordinate = phone_coordinates.filtered(
                lambda c: c.coordinate_type == 'fax')
            fax_coordinate |= fix_coordinate.filtered(lambda f: f.also_for_fax)
            fax_coordinate = fax_coordinate.with_prefetch(self._prefetch)
            mobile_coordinate = phone_coordinates.filtered(
                lambda c: c.coordinate_type == 'mobile')
            mobile_coordinate = mobile_coordinate.with_prefetch(self._prefetch)

            if any(fix_coordinate.mapped("vip")):
                fix = vip
            else:
                fix = first(fix_coordinate).phone_id.name
            if any(mobile_coordinate.mapped("vip")):
                mobile = vip
            else:
                mobile = first(mobile_coordinate).phone_id.name
            if any(fax_coordinate.mapped("vip")):
                fax = vip
            else:
                fax = first(fax_coordinate).phone_id.name
            vip_group = 'mozaik_coordinate.res_groups_coordinate_vip_reader'
            if not first(fix_coordinate).vip or self.user_has_groups(vip_group):
                record.fix_coordinate_id = first(fix_coordinate)
            if not first(mobile_coordinate).vip or self.user_has_groups(vip_group):
                record.mobile_coordinate_id = first(mobile_coordinate)
            if not first(fax_coordinate).vip or self.user_has_groups(vip_group):
                record.fax_coordinate_id = first(fax_coordinate)
            record.phone = fix
            record.mobile = mobile
            record.fax = fax
