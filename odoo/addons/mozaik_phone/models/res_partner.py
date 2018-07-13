# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import except_orm
# Local imports
from .phone_phone import PHONE_AVAILABLE_TYPES, phone_available_types

class ResPartner(models.Model):

    _inherit = 'res.partner'

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    @api.multi
    @api.depends('phone_coordinate_ids')
    def _get_main_phone_coordinate_ids(self):
        """
        ==============================
        _get_main_phone_coordinate_ids
        ==============================
        Reset *_coordinate_id fields with corresponding main phone coordinate
        ids
        """
        # TODO sudo
        coord_obj = self.env['phone.coordinate'].sudo()
        coordinates = coord_obj.search(
            [('partner_id', 'in', self.ids),
             ('is_main', '=', True),
             # ('active', '<=', True)]) ??
             ('active', '=', True)])
        for coord in coordinates: # TODO sudo
            if coord.active == coord.partner_id.active:
                if coord.phone_id.also_for_fax:
                    coord.partner_id.fax_coordinate_id = coord
                coord.partner_id['%s_coordinate_id' % coord.coordinate_type] = coord.id

    @api.multi
    @api.depends('phone_coordinate_ids')
    def _get_main_phone_numbers(self, coordinate_type):
        """
        =======================
        _get_main_phone_numbers
        =======================
        Reset main phone number field for a given phone type
        """
        if not coordinate_type or coordinate_type not in phone_available_types:
            raise except_orm(
                _('Validate Error'),
                _('Invalid phone type: "%s"!') % coordinate_type)

        if coordinate_type == 'fax':
            domain = [
                '|',
                ('coordinate_type', '=', 'fax'),
                '&',
                ('coordinate_type', '=', 'fix'),
                ('also_for_fax', '=', True)]
        else:
            domain = [('coordinate_type', '=', coordinate_type)]
        # TODO sudo
        coord_obj = self.env['phone.coordinate'].sudo()
        coordinates = coord_obj.search(
            [('partner_id', 'in', self.ids),
             ('is_main', '=', True),
             ('active', '<=', True)] + domain)
        for coord in coordinates:
            if coord.active == coord.partner_id.active:
                val = ''
                if coord.vip:
                    val = 'VIP'
                else:
                    val = coord.phone_id.name
                coord.partner_id[coordinate_type if coordinate_type != "fix" else "phone"] = val

    # TODO store={}, don't really know the behavoir with that
    # _phone_store_triggers = {
    #     'phone.coordinate': (
    #         lambda self, cr, uid, ids, context=None:
    #         self.pool['phone.coordinate'].get_linked_partners(
    #             cr, uid, ids, context=context), [
    #             'partner_id', 'phone_id', 'is_main', 'vip',
    #             'unauthorized', 'active'], 10),
    #     'phone.phone': (
    #         lambda self, cr, uid, ids, context=None:
    #         self.pool['phone.phone'].get_linked_partners(
    #             cr, uid, ids, context=context), [
    #             'name', 'type', 'also_for_fax'], 10), }

    phone_coordinate_ids = fields.One2many(
        'phone.coordinate', 'partner_id', 'Phone Coordinates', copy=False,
        domain=[('active', '=', True)], context={'force_recompute': True}) # TODO force_recompute still usefull? (don't know what it does)
    phone_coordinate_inactive_ids = fields.One2many(
        'phone.coordinate', 'partner_id', 'Phone Coordinates', copy=False,
        domain=[('active', '=', False)])

    fix_coordinate_id = fields.Many2one(
        compute=_get_main_phone_coordinate_ids, string='Phone',
        comodel_name="phone.coordinate")
    mobile_coordinate_id = fields.Many2one(
        compute=_get_main_phone_coordinate_ids, string='Mobile',
        comodel_name="phone.coordinate")
    fax_coordinate_id = fields.Many2one(
        compute=_get_main_phone_coordinate_ids, string='Fax',
        comodel_name="phone.coordinate")


    # Standard fields redefinition
    phone = fields.Char(
        compute=lambda s: s._get_main_phone_numbers(coordinate_type='fix'), string='Phone', index=True)
        # store=_phone_store_triggers), TODO
    mobile = fields.Char(
        compute=lambda s: s._get_main_phone_numbers(coordinate_type='mobile'), string='Mobile', index=True)
        # store=_phone_store_triggers), TODO
    fax = fields.Char(
        compute=lambda s: s._get_main_phone_numbers(coordinate_type='fax'), string='Fax', index=True)
        # store=_phone_store_triggers), TODO


# orm methods

    # def copy_data(self, default=None): # TODO copy=False field def (to test)
    #     """
    #     Do not copy o2m fields.
    #     """
    #     default = default or {}
    #     default.update({
    #         'phone_coordinate_ids': [],
    #         'phone_coordinate_inactive_ids': [],
    #     })
    #     res = super().copy_data(default=default)
    #     return res
