# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
import psycopg2

from odoo.tests.common import SavepointCase

from odoo import exceptions
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, mute_logger


class TestPartnerInvolvement(SavepointCase):

    def setUp(self):
        super().setUp()
        self.paul = self.browse_ref('mozaik_involvement.res_partner_bocuse')

    def test_add_interests_on_involvement_creation(self):
        '''
        Check for interests propagation when creating an involvement
        '''
        # get a partner
        paul = self.paul
        # get an involvement category
        cat = self.browse_ref(
            'mozaik_involvement.partner_involvement_category_demo_1')
        # create a term
        term_id = self.env['thesaurus.term'].create({
            'name': 'Bonne Bouffe !',
        })
        # add it on category
        cat.write({
            'interest_ids': [(4, term_id.id)],
        })
        self.env['partner.involvement'].create({
            'partner_id': paul.id,
            'involvement_category_id': cat.id,
        })
        self.assertIn(cat.interest_ids, paul.interest_ids)
        return

    def test_multi(self):
        """
        Check for multiple involvements
        """
        # get a partner
        paul = self.paul
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
