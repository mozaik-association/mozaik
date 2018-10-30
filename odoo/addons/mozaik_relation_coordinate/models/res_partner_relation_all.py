# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    email_coordinate_id = fields.Many2one(
        comodel_name='email.coordinate',
        string='Email Coordinate',
        domain=(
            "["
            "('partner_id', '=', this_partner_id),"
            "('is_main', '=', False),"
            "]"
        ),
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name='postal.coordinate',
        string='Postal Coordinate',
        domain=(
            "["
            "('partner_id', '=', this_partner_id),"
            "('is_main', '=', False),"
            "]"
        ),
    )
    fix_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Fix Coordinate',
        domain=(
            "["
            "('partner_id', '=', this_partner_id), "
            "('is_main', '=', False),"
            "('coordinate_type', '=', 'fix'),"
            "]"
        ),
    )
    mobile_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Mobile Coordinate',
        domain=(
            "["
            "('partner_id', '=', this_partner_id), "
            "('is_main', '=', False),"
            "('coordinate_type', '=', 'mobile'),"
            "]"
        ),
    )
    fax_coordinate_id = fields.Many2one(
        comodel_name='phone.coordinate',
        string='Fax Coordinate',
        domain=(
            "["
            "('partner_id', '=', this_partner_id), "
            "('is_main', '=', False),"
            "'|', "
            "('coordinate_type', '=', 'fax'), "
            "('also_for_fax', '=', True),"
            "]"
        ),
    )
    note = fields.Text(
        string='Notes',
    )
    create_date = fields.Datetime(
        string='Created on',
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
    )

    @api.model_cr_context
    def _auto_init(self):
        """
        Just to regenerate the view when data model change here
        """
        return super()._auto_init()

    @api.model
    def _get_coordinate_fields(self):
        """ retrieve coordinate fields define here above """
        flds = [
            n for (n, f)
            in self._fields.items()
            if f.type == 'many2one' and f.comodel_name in (
                'phone.coordinate', 'postal.coordinate', 'email.coordinate',
            )
        ]
        return flds

    @api.model
    def _get_additional_relation_columns(self):
        """ add a new columns in SQL view """
        res = super()._get_additional_relation_columns()
        added_fields = (
            ', rel.note'
            ', rel.create_date'
        )
        for fld in self._get_coordinate_fields():
            added_fields += ', rel.%s' % fld
        return "%s%s" % (res, added_fields)

    @api.multi
    def toggle_active(self):
        """ Update date_end instead of active """
        actives = self.filtered('active')
        inactives = self.filtered(lambda s: not s.active)
        yesterday = (
            datetime.date.today() - datetime.timedelta(days=1)).strftime(
                fields.DATE_FORMAT)
        actives.write({'date_end': yesterday})
        inactives.write({'date_end': False})

    @api.model
    def _correct_vals(self, vals, type_selection):
        """remove coordinates from values"""
        vals = super()._correct_vals(vals, type_selection)
        if type_selection.is_inverse:
            for key in self._get_coordinate_fields():
                vals.pop(key, None)
        return vals

    @api.onchange('type_selection_id')
    def onchange_type_selection_id(self):
        """ Refresh is_inverse on the form when changing type """
        self.ensure_one()
        result = super().onchange_type_selection_id()
        if self.type_selection_id:
            self.is_inverse = self.type_selection_id.is_inverse
        else:
            self.is_inverse = False
        return result
