# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp import tools


def _get_document_types(s, cr, uid, context=None):
    cr.execute("SELECT model, name from ir_model WHERE model IN \
                ('sta.mandate', 'int.mandate', 'ext.mandate') ORDER BY name")
    return cr.fetchall()


class generic_mandate(orm.Model):
    _name = "generic.mandate"
    _description = 'Generic Mandate'
    _auto = False

    _discriminant_field = 'partner_id'

    def _is_discriminant_m2o(self):
        return isinstance(self._columns[self._discriminant_field],
                          fields.many2one)

    _columns = {
        'id': fields.integer('ID'),
        'model': fields.char('Models'),
        'mandate_id': fields.integer('Mandate ID', group_operator='min'),
        'mandate_ref': fields.reference('Mandate Reference',
                                        selection=_get_document_types),
        'mandate_category_id': fields.many2one('mandate.category',
                                               'Mandate Category'),
        'assembly_name': fields.char("Assembly"),
        'partner_id': fields.many2one('res.partner', 'Representative'),
        'start_date': fields.date('Start Date'),
        'deadline_date': fields.date('Deadline Date'),
        'is_duplicate_detected': fields.boolean('Incompatible Mandate'),
        'is_duplicate_allowed': fields.boolean('Allowed Incompatible Mandate'),
    }

    _rec_name = 'mandate_ref'
    _order = 'partner_id, mandate_category_id'

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'generic_mandate')
        cr.execute("""
            create or replace view generic_mandate as (
                    SELECT 'int.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('int.mandate,', mandate.id) as mandate_ref,
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM int_mandate  AS mandate
                        JOIN int_assembly AS assembly
                          ON assembly.id = mandate.int_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'sta.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('sta.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM sta_mandate  AS mandate
                        JOIN sta_assembly AS assembly
                          ON assembly.id = mandate.sta_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'ext.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('ext.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM ext_mandate  AS mandate
                        JOIN ext_assembly AS assembly
                          ON assembly.id = mandate.ext_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL
            )
        """)

# view methods: onchange, button

    def button_view_mandate(self, cr, uid, ids, context=None):
        """
        ======
        button_view_mandate
        ======
        View mandates in its form view depending on model
        """
        (model, m_id) = self.read(cr, uid, ids[0], ['mandate_ref'],
                                  context=context)['mandate_ref'].split(',')
        return self.pool[model].display_object_in_form_view(cr, uid, int(m_id),
                                                            context=context)
