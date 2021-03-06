# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_email, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_email is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_email is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_email.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
from openerp import fields
from openerp.addons.mozaik_coordinate.tests.test_bounce import test_bounce
from anybox.testing.openerp import SharedSetupTransactionCase

DESC = 'Bad Coordinate'

class test_email_bounce(test_bounce, SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/email_data.xml',
    )

    _module_ns = 'mozaik_email'

    def setUp(self):
        super(test_email_bounce, self).setUp()

        # instanciate members of abstract test
        self.model_coordinate = self.registry('email.coordinate')
        self.model_coordinate_id = self.ref(
            '%s.email_coordinate_thierry_two' % self._module_ns)
        self.model_coordinate_id2 = self.ref(
            '%s.email_coordinate_thierry_one' % self._module_ns)

    def test_reset_bounce(self):
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
        coord2 = self.model_coordinate.browse(
            cr, uid, self.model_coordinate_id2,
            context=context)
        self.assertFalse(coord.bounce_counter)

        # 2/ Create wizard record
        wiz_id = self.create_bounce_data(2)
        coord2.bounce_counter = 1

        # 3/ Execute wizard
        self.model_wizard.update_bounce_datas(
            cr, uid, [wiz_id], context=context)
        self.assertEqual(
            coord.bounce_counter, 2)
        self.assertEqual(
            coord.bounce_description, DESC)
        self.assertEqual(coord.first_bounce_date, coord.bounce_date)

        # 4/ Reset counter
        check_bounce_date = datetime.today() - timedelta(
            days=int(self.env['ir.config_parameter'].get_param(
                'bounce_counter_reset_time_delay')))
        self.env["mail.mail.statistics"].create({
            "res_id": coord.id,
            "model": "email.coordinate",
            "sent": check_bounce_date,
            "bounced": check_bounce_date + timedelta(days=1),
        })
        self.env["mail.mail.statistics"].create({
            "res_id": coord2.id,
            "model": "email.coordinate",
            "sent": check_bounce_date,
        })
        coord2.bounce_date = check_bounce_date - timedelta(days=1)

        self.env['mail.mass_mailing'].search([]).write({
            "sent_date": fields.Datetime.to_string(check_bounce_date)})
        self.env["email.coordinate"].update_bounce_counter_mass_mailing()
        self.assertEqual(
            coord.bounce_counter, 2)
        self.assertEqual(
            coord2.bounce_counter, 0)
