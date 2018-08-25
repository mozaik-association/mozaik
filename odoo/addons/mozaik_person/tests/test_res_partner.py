# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def test_res_partner_names(self):
        """
        Test the overriding of name_get method to compute display_name
        Test also select_name, printable_name and technical_name
        """
        # create a partner
        b16 = self.env['res.partner'].new({
            'lastname': 'Ratzinger',
            'firstname': 'Joseph',
        })
        self.assertEqual(b16.name, b16.select_name)
        self.assertEqual(b16.display_name, b16.select_name)
        self.assertEqual('Joseph Ratzinger', b16.printable_name)
        self.assertEqual('ratzingerjoseph', b16.technical_name)
        # add an identifier
        b16.identifier = 666
        self.assertEqual(b16.name, b16.select_name)
        self.assertEqual('666-Ratzinger Joseph', b16.display_name)
        # add usual names
        b16.update({
            'usual_lastname': 'XVI',
            'usual_firstname': 'Benoît',
            'identifier': False,
        })
        self.assertNotEqual(b16.name, b16.select_name)
        self.assertEqual('XVI Benoît (Ratzinger Joseph)', b16.select_name)
        self.assertEqual(b16.select_name, b16.display_name)
        self.assertEqual('Benoît XVI', b16.printable_name)
        self.assertEqual('xvibenoitratzingerjoseph', b16.technical_name)
        # make nams = usual names
        b16.update({
            'lastname': 'XVI',
            'firstname': 'Benoît',
        })
        self.assertEqual(b16.name, b16.select_name)
        self.assertEqual(b16.select_name, b16.display_name)
        self.assertEqual('XVI Benoît', b16.select_name)
        self.assertEqual('Benoît XVI', b16.printable_name)
        self.assertEqual('xvibenoit', b16.technical_name)
        # convert it to a company
        b16.update({
            'is_company': True,
            'lastname': 'Chapelle Sixtine',
            'firstname': False,
            'acronym': 'B16',
            'identifier': 777,
            'email': 'b16@rome.it',
        })
        self.assertNotEqual(b16.name, b16.select_name)
        self.assertEqual('Chapelle Sixtine (B16)', b16.select_name)
        self.assertEqual('777-Chapelle Sixtine (B16)', b16.display_name)
        self.assertEqual(b16.name, b16.printable_name)
        self.assertEqual('chapellesixtineb16', b16.technical_name)
        self.assertEqual('777-Chapelle Sixtine (B16)', b16.name_get()[0][1])
        self.assertEqual(
            'Chapelle Sixtine <b16@rome.it>',
            b16.with_context(show_email=True).name_get()[0][1])
        return

    def test_res_partner_duplicates(self):
        """
        Test duplicate detection, permission and repairing
        """
        # get 2 partners
        nouvelobs = self.browse_ref('mozaik_person.res_partner_demo_01')
        nouvelobs_bis = self.browse_ref('mozaik_person.res_partner_demo_02')
        partners = nouvelobs | nouvelobs_bis

        # check for reference data
        for partner in partners:
            bools = [
                not partner.active,
                not partner.is_company,
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # update nouvelobs_bis=nouvelobs => duplicates: 2 detected, 0 allowed
        nouvelobs_bis.name = 'Nouvel Observateur'
        for partner in partners:
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # allow duplicates => duplicates: 0 detected, 2 allowed
        ctx = {
            'active_model': 'res.partner',
            'active_ids': partners.ids,
        }
        wizard = self.env['allow.duplicate.wizard'].with_context(ctx).new()
        wizard.button_allow_duplicate()
        for partner in partners:
            bools = [
                partner.is_duplicate_detected,
                not partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # undo allow one duplicate => duplicates: 2 detected, 0 allowed
        nouvelobs.button_undo_allow_duplicate()
        for partner in partners:
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # create one more nouvelobs => duplicates: 3 detected, 0 allowed
        nouvelobs_ter = nouvelobs.create(
            {'name': nouvelobs.name, 'is_company': True})
        for partner in (partners | nouvelobs_ter):
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # invalidate one partner => duplicates: 2 detected, 0 allowed
        nouvelobs_ter.toggle_active()
        for partner in partners:
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))
        for partner in nouvelobs_ter:
            bools = [
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # update nouvelobs_bis => duplicates: 0 detected, 0 allowed
        nouvelobs_bis.name = 'Nouvel Observateur (Economat)'
        for partner in partners:
            bools = [
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # reactivate nouvelobs_ter => duplicates: 2 detected, 0 allowed
        nouvelobs_ter.toggle_active()
        for partner in (nouvelobs | nouvelobs_ter):
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        return

    def test_invalidate_active_relation(self):
        """
        Test invalidation of active relations (not inherited
        from mozaik abstract model) and _check_invalidate constraint
        """
        # create a user
        user = self.env['res.users'].create({
            'name': 'Fabius Laurent',
            'login': 'FL',
        })

        # invalidate user's partner
        user.partner_id.toggle_active()
        self.assertFalse(user.active)

        # reactivate user: NOK
        user.partner_id.toggle_active()
        return

    def test_res_partner_duplicates_with_birthdate(self):
        """
        Test duplicate detection, permission and repairing
        with birthdate
        """
        # get 2 partners
        dany1 = self.browse_ref('mozaik_person.res_partner_demo_03')
        dany2 = self.browse_ref('mozaik_person.res_partner_demo_04')
        partners = dany1 | dany2

        # check for reference data
        for partner in partners:
            bools = [
                not partner.active,
                partner.is_company,
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # update birthdate dany2=dany1 => 2 detected, 0 allowed
        dany2.birthdate_date = dany1.birthdate_date
        for partner in partners:
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # update dany1's birthdate=1990-10-10 => 0 detected, 0 allowed
        dany1.birthdate_date = '1990-10-10'
        for partner in partners:
            bools = [
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # add a new dany without birthdate => 3 detected, 0 allowed
        dany3 = dany1.create({'name': 'Boon Dany'})
        for partner in (partners | dany3):
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))

        # update dany3's birthdate=1990-10-10 => 2 detected, 0 allowed
        dany3.birthdate_date = dany1.birthdate_date
        for partner in (dany1 | dany3):
            bools = [
                not partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))
        for partner in dany2:
            bools = [
                partner.is_duplicate_detected,
                partner.is_duplicate_allowed,
            ]
            self.assertFalse(any(bools))
        return

    def test_check_identifier(self):
        """
        Test identifier unicity constraint
        """
        # get 2 partners
        dany1 = self.browse_ref('mozaik_person.res_partner_demo_03')
        dany2 = self.browse_ref('mozaik_person.res_partner_demo_04')

        # update identifier of dany1=dany2: NOK
        with self.assertRaises(exceptions.ValidationError):
            dany1.identifier = dany2.identifier

    def test_update_identifier_sequence(self):
        """
        Test method to update the partner ir_sequence
        """
        # get the partner with MAX(identifier)
        partner = self.env['res.partner'].search(
            [], limit=1, order='identifier desc')
        partner.identifier += 47

        # update the sequence
        self.env['res.partner']._update_identifier_sequence()

        # get and check the sequence
        next_ident = self.env['ir.sequence'].next_by_code('res.partner')
        self.assertEqual('%s' % (partner.identifier + 1), next_ident)

        # create a new partner and check its identifier
        patriiiiick = partner.create({'name': 'Patriiiiick Bruel'})
        self.assertEqual(partner.identifier + 2, patriiiiick.identifier)
        return
