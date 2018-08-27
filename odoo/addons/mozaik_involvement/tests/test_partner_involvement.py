# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
import psycopg2

from odoo.tests.common import TransactionCase

from odoo import exceptions
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, mute_logger


class TestPartnerInvolvement(TransactionCase):

    def _new_partner(self):
        return self.env['res.partner'].create({
            'name': 'Paul Bocuse',
        })

    def test_add_interests_on_involvement_creation(self):
        '''
        Check for interests propagation when creating an involvement
        '''
        # create a partner
        paul = self._new_partner()
        # get an involvement category
        cat = self.browse_ref(
            'mozaik_involvement.partner_involvement_category_demo_1')
        # add terms to category
        # cat.write({
        # })
        self.env['partner.involvement'].create({
            'partner_id': paul.id,
            'involvement_category_id': cat.id,
        })
        # for term in cat.interests_m2m_ids:
        #     self.assertIn(term, paul.interest_ids)
        return

    def test_multi(self):
        """
        Check for multiple involvements
        """
        # create a partner
        paul = self._new_partner()
        # get an involvement category
        cat = self.browse_ref(
            'mozaik_involvement.partner_involvement_category_demo_1')
        # create an involvement
        involvement = self.env['partner.involvement'].create({
            'partner_id': paul.id,
            'involvement_category_id': cat.id,
        })
        # check for effective_time
        self.assertFalse(involvement.effective_time)
        # copy it: NOK
        with self.assertRaises(exceptions.UserError):
            involvement.copy()
        # allow miltiple involvements
        cat.allow_multi = True
        # check for effective_time
        self.assertTrue(involvement.effective_time)
        involvement.unlink()
        # create a new involvement
        now = (datetime.now() + timedelta(hours=-1)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        involvement = self.env['partner.involvement'].create({
            'partner_id': paul.id,
            'involvement_category_id': cat.id,
            'effective_time': now,
        })
        # copy it: OK
        involvement.copy()
        # create an already existing involvement: NOK
        with self.assertRaises(psycopg2.IntegrityError), \
                mute_logger('odoo.sql_db'):
            self.env['partner.involvement'].create({
                'partner_id': paul.id,
                'involvement_category_id': cat.id,
                'effective_time': now,
            })
        return

    def test_onchange_type(self):
        """
        Check for allow_multiple when changing involvment type
        """
        # create an involvement category
        cat = self.env['partner.involvement.category'].new({
            'name': 'Semeur, vaillants du rêve...',
        })
        # Change type to donation
        cat.involvement_type = 'donation'
        cat._onchange_involvement_type()
        self.assertTrue(cat.allow_multi)
        # Change type to another type
        cat.involvement_type = 'voluntary'
        cat._onchange_involvement_type()
        self.assertFalse(cat.allow_multi)
        return
