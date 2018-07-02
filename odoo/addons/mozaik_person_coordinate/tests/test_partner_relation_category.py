# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase
import logging

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class test_partner_relation_category(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_coordinate/tests/data/coordinate_category_data.xml',
        'data/relation_data.xml',
    )

    _module_ns = 'mozaik_person_coordinate'

    def setUp(self):
        super(test_partner_relation_category, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        self.model_partner_relation_category = self.registry(
            'partner.relation.category')

    def test_name_get(self):
        """
        This method test that for a given object key in context,
        the method name_get of partner_relation_category will return either
        subject_name or object_name depending context['object'] False or Not
        """
        rec_relation = self.browse_ref(
            "mozaik_person_coordinate.partner_relation")
        res = self.model_partner_relation_category.name_get(
            self.cr, SUPERUSER_ID, [
                rec_relation.partner_relation_category_id.id], context=None)
        self.assertEqual(
            'is employee of',
            res[0][1],
            "Without context: should be subject name")
        res = self.model_partner_relation_category.name_get(
            self.cr, SUPERUSER_ID, [
                rec_relation.partner_relation_category_id.id], context={
                'object': False})
        self.assertEqual(
            'is employee of',
            res[0][1],
            "Without object false into context: should be subject name")
        res = self.model_partner_relation_category.name_get(
            self.cr, SUPERUSER_ID, [
                rec_relation.partner_relation_category_id.id], context={
                'object': True})
        self.assertEqual(
            'employs',
            res[0][1],
            "With object into context: should be object name")

    def test_check_relation_qualification(self):
        rec_relation = self.browse_ref(
            "mozaik_person_coordinate.partner_relation")
        category_id = rec_relation.partner_relation_category_id.id
        self.assertRaises(
            orm.except_orm,
            rec_relation._model.create,
            self.cr,
            SUPERUSER_ID,
            {'object_partner_id': rec_relation.subject_partner_id.id,
             'subject_partner_id': rec_relation.object_partner_id.id,
             'partner_relation_category_id': category_id})
        self.assertRaises(
            orm.except_orm,
            rec_relation._model.create,
            self.cr,
            SUPERUSER_ID,
            {
                'object_partner_id': rec_relation.subject_partner_id.id,
                'subject_partner_id': rec_relation.subject_partner_id.id,
                'partner_relation_category_id': category_id})
