# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestUsualFirstname(TransactionCase):

    def test_compute_and_inverse(self):
        '''
        Check for result of both compute and inverse name methods
        rmk: names_order=last_first
        '''
        poutine = self.env['res.partner'].create({
            'name': 'Poutine Vladimir',
        })
        # native result from partner_firstname module
        self.assertEqual('Poutine Vladimir', poutine.name)
        self.assertEqual('Vladimir', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertFalse(poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)
        # add an usual_firstname
        poutine.usual_firstname = 'Vladinou'
        self.assertEqual('Poutine Vladinou', poutine.name)
        self.assertEqual('Vladimir', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertEqual('Vladinou', poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)
        # add an usual_lastname
        poutine.usual_lastname = 'Poutinou'
        self.assertEqual('Poutinou Vladinou', poutine.name)
        self.assertEqual('Vladimir', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertEqual('Vladinou', poutine.usual_firstname)
        self.assertEqual('Poutinou', poutine.usual_lastname)
        # change name
        poutine.name = 'Sarko Nico'
        self.assertEqual('Sarko Nico', poutine.name)
        self.assertEqual('Vladimir', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertEqual('Nico', poutine.usual_firstname)
        self.assertEqual('Sarko', poutine.usual_lastname)
        # change firstname again
        poutine.firstname = 'Lioudmila'
        self.assertEqual('Sarko Nico', poutine.name)
        self.assertEqual('Lioudmila', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertEqual('Nico', poutine.usual_firstname)
        self.assertEqual('Sarko', poutine.usual_lastname)
        # change name again
        poutine.name = 'Poutine Lioudmila'
        self.assertEqual('Poutine Lioudmila', poutine.name)
        self.assertEqual('Lioudmila', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertFalse(poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)
        # change name again
        poutine.write({'firstname': False, 'usual_firstname': 'Vladimir'})
        poutine.name = 'Poutine Vladimir'
        self.assertEqual('Poutine Vladimir', poutine.name)
        self.assertEqual('Vladimir', poutine.firstname)
        self.assertEqual('Poutine', poutine.lastname)
        self.assertFalse(poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)

        return
