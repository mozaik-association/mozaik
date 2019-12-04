# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MandateCategory(models.Model):

    _inherit = 'mandate.category'

    female_name = fields.Char(
        required=True,
        index=True,
        track_visibility='onchange',
    )

    @api.multi
    def name_get(self):
        """
        Returns female_name if context contains gender=female
        """
        if self._context.get('gender') == 'female':
            res = []
            convert = self._fields['female_name'].convert_to_display_name
            for record in self:
                res.append((record.id, convert(record.female_name, record)))
            return res
        return super().name_get()

    @api.model
    def _name_search(
            self, name='', args=None, operator='ilike', limit=100,
            name_get_uid=None):
        """
        Search on female_name or name depending on the context:
        * if gender not in ctx => search on both fields
        * if gender=female => only female_name
        * else only name
        """
        if 'gender' in self._context and self._context['gender'] != 'female':
            return super()._name_search(
                name=name, args=args,
                operator=operator, limit=limit,
                name_get_uid=name_get_uid)
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            if 'gender' not in self._context:
                args += [('|')]
                args += [('name', operator, name)]
            args += [('female_name', operator, name)]
        access_rights_uid = name_get_uid or self._uid
        ids = self._search(
            args, limit=limit, access_rights_uid=access_rights_uid)
        recs = self.browse(ids)
        return recs.sudo(access_rights_uid).name_get()

    @api.multi
    def copy_data(self, default=None):
        res = super().copy_data(default=default)

        res[0].update({
            'female_name': _('%s (copy)') % res[0].get('female_name'),
        })
        return res
