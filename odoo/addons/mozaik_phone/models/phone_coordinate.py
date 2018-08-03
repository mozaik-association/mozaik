# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PhoneCoordinate(models.Model):

    _name = 'phone.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Phone Coordinate'

    # TODO
    _track = {
        'failure_counter': {
            'mozaik_phone.phone_failure_notification': lambda self,
                                                              cr,
                                                              uid,
                                                              obj,
                                                              ctx=None: obj.failure_counter,
        },
    }

    _discriminant_field = 'phone_id'
    _undo_redirect_action = 'mozaik_phone.phone_coordinate_action'

    # TODO I don't understand the store={}...
    # _type_store_triggers = {
    #     'phone.coordinate': (
    #         lambda self, cr, uid, ids, context=None: ids, ['phone_id'], 10),
    #     'phone.phone': (
    #         lambda self, cr, uid, ids, context=None:
    #         self.pool['phone.phone']._get_linked_coordinates(
    #             cr, uid, ids, context=context), [
    #             'type', 'also_for_fax'], 10), }

    phone_id = fields.Many2one(
        'phone.phone',
        string='Phone',
        required=True,
        readonly=True,
        index=True)
    coordinate_type = fields.Selection(
        related='phone_id.type',
        readonly=True, default =False)
        # store=_type_store_triggers), TODO
    also_for_fax = fields.Boolean(
        related='phone_id.also_for_fax',
        readonly=True,)
        # store=_type_store_triggers), TODO

    _rec_name = _discriminant_field

    # constraints

    _unicity_keys = 'partner_id, phone_id'

    # orm methods

    @api.model
    def create(self, vals):
        if not vals.get('coordinate_type'):
            phone = self.env['phone.phone'].browse(vals['phone_id'])
            vals['coordinate_type'] = phone.type
        return super().create(vals)
