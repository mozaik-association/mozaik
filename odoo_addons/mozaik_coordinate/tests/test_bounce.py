# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import psycopg2

from openerp.addons.mozaik_base import testtool

DESC = 'Bad Coordinate'

class test_bounce(object):
    """ unittest2 run test for the abstract class too
    resolved with a dual inherit on the abstract and the common.NAME
    """

    def setUp(self):
        super(test_bounce, self).setUp()

        self.model_wizard = self.registry('bounce.editor')

        self.context = {}

        # members to instanciate by real test
        self.model_coordinate = None
        self.model_coordinate_id = None

    def create_bounce_data(self, inc):
        """
        Create a wizard record
        """
        cr, uid, context = self.cr, self.uid, self.context

        context.update({
            'active_ids': [self.model_coordinate_id],
            'active_model': self.model_coordinate._name,
            'default_model': self.model_coordinate._name,
        })
        wiz_vals = {
            'increase': inc,
            'description': DESC,
        }
        wiz_id = self.model_wizard.create(cr, uid, wiz_vals, context=context)
        return wiz_id

    def test_add_bounce(self):
        """
        1/ test reference data
        2/ create a valid wz
        3/ execute it and test the new counter value
        4/ reset the counter and test its value
        5/ create an invalid wz
        """
        cr, uid, context = self.cr, self.uid, self.context

        # 1/ Check for reference data
        coord = self.model_coordinate.browse(
            cr, uid, self.model_coordinate_id,
            context=context)
        self.assertFalse(coord.bounce_counter, '')

        # 2/ Create wizard record
        wiz_id = self.create_bounce_data(2)

        # 3/ Execute wizard
        self.model_wizard.update_bounce_datas(
            cr, uid, [wiz_id], context=context)
        self.assertEqual(
            coord.bounce_counter, 2,
            '')
        self.assertEqual(
            coord.bounce_description, DESC,
            'Bad Coordinate')
        self.assertEqual(coord.first_bounce_date, coord.bounce_date)

        # 4/ Reset counter
        self.model_coordinate.button_reset_counter(
            cr, uid, self.model_coordinate_id, context=context)
        self.assertFalse(coord.bounce_counter, '')
        self.assertFalse(coord.bounce_date, False)
        self.assertFalse(coord.first_bounce_date, False)

        # 5/ Try to create an invalid wizard record
        with testtool.disable_log_error(cr):
            self.assertRaises(
                psycopg2.IntegrityError, self.create_bounce_data, -2)
