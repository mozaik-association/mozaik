# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta
from uuid import uuid4

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMembershipLine(TransactionCase):
    def setUp(self):
        super(TestMembershipLine, self).setUp()
        self.membership_obj = self.env["membership.line"]
        self.partner_obj = self.env["res.partner"]
        self.state_obj = self.env["membership.state"]
        self.instance_obj = self.env["int.instance"]
        self.product_obj = self.env["product.product"]
        self.instance = self.env.ref("mozaik_structure.int_instance_03")
        self.partner_marc = self.env.ref("mozaik_membership.res_partner_marc")
        self.product_subscription = self.env.ref(
            "mozaik_membership.membership_product_isolated"
        )
        self.product_free = self.env.ref("mozaik_membership.membership_product_free")

    def test_generate_membership_reference(self):
        """
        Check if the membership reference match the arbitrary pattern:
        'MS: year(given ref_date)/<instance-id>/<partner-id>'
        """
        partner = self.partner_marc
        instance = self.instance
        ref_date = fields.Date.today()
        # generate the reference
        genref = self.membership_obj._generate_membership_reference(
            partner, instance, ref_date=ref_date
        )
        year = fields.Date.from_string(ref_date).year
        ref = "MS: %s/%s/%s" % (year, instance.id, partner.id)
        self.assertEqual(genref, ref)

    def test_get_subscription_price1(self):
        """
        Test the _get_subscriptioon price
        :return:
        """
        partner = self.partner_marc
        instance = self.instance
        # get the price
        price = self.membership_obj._get_subscription_price(
            self.product_free, partner=partner, instance=instance
        )
        self.assertAlmostEqual(price, self.product_free.list_price)

    def test_get_subscription_price2(self):
        """
        Test the _get_subscription price
        :return:
        """
        membership_obj = self.membership_obj
        partner = self.partner_marc
        instance = self.instance
        price = 1256.369
        # update the product price
        self.product_free.write(
            {
                "list_price": price,
            }
        )
        # Use the precision defined on the price field
        precision = membership_obj._fields.get("price").get_digits(self.env)[1]
        # get the price
        result_price = membership_obj._get_subscription_price(
            self.product_free, partner=partner, instance=instance
        )
        self.assertAlmostEqual(price, result_price, places=precision)

    def _get_membership_line_values(
        self,
        date_from=False,
        date_to=False,
        partner=False,
        state=False,
        instance=False,
        price=False,
        ref=False,
        product=False,
    ):
        """

        :param date_from: date
        :param date_to: date
        :param partner: res.partner recordset
        :param state: membership.state recordset
        :param instance: int.instance recordset
        :param price: float
        :param ref: str
        :param product: product.product recordset
        :return: dict
        """
        if isinstance(partner, bool):
            partner = self.partner_obj.browse()
        if isinstance(state, bool):
            state = self.state_obj.browse()
        if isinstance(instance, bool):
            instance = self.instance_obj.browse()
        if isinstance(product, bool):
            product = self.product_obj.browse()
        values = {
            "date_from": date_from,
            "date_to": date_to,
            "partner_id": partner.id,
            "state_id": state.id,
            "int_instance_id": instance.id,
            "price": price,
            "reference": ref,
            "product_id": product.id,
        }
        return values

    def test_renew1(self):
        """
        Test the renew to ensure that copied values are corrects
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = "2015-06-05"
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.to_string(fields.Date.from_string("2015-11-09"))
        # Renew it (should not create a new membership)
        same_membership = membership._renew(date_from=new_date_from)
        self.assertFalse(same_membership)
        return

    def test_renew2(self):
        """
        Test the renew to ensure that copied values are corrects
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = "2015-06-05"
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # Force False to create a new one instead of updating the existing
        membership.write(
            {
                "active": False,
                "date_to": date_from,
            }
        )
        # We have to transform the date in correct format
        new_date_from = fields.Date.from_string("2015-11-09")
        # The product should be saved before the renew
        theoric_product = partner.subscription_product_id
        # Renew it
        created = membership._renew(date_from=fields.Date.to_string(new_date_from))
        self.assertEqual(created.date_from, new_date_from)
        self.assertEqual(created.partner_id, partner)
        self.assertEqual(created.int_instance_id, instance)
        self.assertEqual(created.product_id, theoric_product)
        # Should be equals because it's a simple renew
        self.assertNotEqual(created, membership)
        return

    def test_renew_with_date1(self):
        """
        Test the renew with the case of the date_from (into membership.line)
        is the date interval (from parameter) where it shouldn't be renewed
        :return:
        """
        self.env["ir.config_parameter"].set_param(
            "membership.no_subscription_renew", "01/01"
        )
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = date.today() - timedelta(days=1)
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.to_string(date.today() + timedelta(days=1))
        # The product should be saved before the renew
        # Renew it
        created = membership._renew(date_from=new_date_from)
        # Due to the date set into parameters, we shouldn't have a new line
        self.assertFalse(created)
        return

    def test_renew_with_date2(self):
        """
        Test the renew with the case of the date_from (into membership.line)
        is > than today so we don't have to renew it
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = fields.Date.from_string(fields.Date.today())
        date_from += timedelta(days=25)
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.today()
        # The product should be saved before the renew
        # Renew it
        created = membership._renew(date_from=new_date_from)
        # Due to the date set into parameters, we shouldn't have a new line
        self.assertFalse(created)
        return

    def test_former_member1(self):
        """
        Test the former member to ensure that copied values are corrects
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 0
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = "2015-06-05"
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.to_string(fields.Date.from_string("2015-11-09"))
        # Former member it (should not create a new membership)
        member = self.env.ref("mozaik_membership.member")
        former_member = self.env.ref("mozaik_membership.former_member")
        same_membership = membership._change_state(
            member, former_member, date_from=new_date_from
        )
        self.assertFalse(same_membership)
        return

    def test_former_member2(self):
        """
        Test the former member to ensure that copied values are corrects
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = self.env.ref("mozaik_membership.member")
        date_from = "2015-06-05"
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # Force False to create a new one instead of updating the existing
        membership.write(
            {
                "active": False,
                "date_to": date_from,
            }
        )
        membership.flush()
        # We have to transform the date in correct format
        new_date_from = fields.Date.from_string("2015-11-09")
        # Former member it
        member = self.env.ref("mozaik_membership.member")
        former_member = self.env.ref("mozaik_membership.former_member")
        created = membership._change_state(
            member, former_member, date_from=fields.Date.to_string(new_date_from)
        )
        self.assertEqual(created.date_from, new_date_from)
        self.assertEqual(created.partner_id, partner)
        self.assertEqual(created.int_instance_id, instance)
        # Should be equals because it's a simple former member
        self.assertNotEqual(created, membership)
        return

    def test_former_member_with_date1(self):
        """
        Test the former member with the case of the date_from
        (into membership.line) is the date interval (from parameter) where it
        shouldn't be former member
        :return:
        """
        self.env["ir.config_parameter"].set_param(
            "membership.no_subscription_renew", "01/01"
        )
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = date.today() - timedelta(days=1)
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.to_string(date.today() + timedelta(days=1))
        # The product should be saved before the former member
        # Former member it
        member = self.env.ref("mozaik_membership.member")
        former_member = self.env.ref("mozaik_membership.former_member")
        created = membership._change_state(
            member, former_member, date_from=new_date_from
        )
        # Due to the date set into parameters, we shouldn't have a new line
        self.assertFalse(created)
        return

    def test_former_member_with_date2(self):
        """
        Test the former member with the case of the date_from
        (into membership.line) is > than today so we don't have to
        former member it
        :return:
        """
        membership_obj = self.membership_obj
        # For the current test, remove every other membership.line records
        membership_obj.search([]).unlink()
        price = 500
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = fields.Date.from_string(fields.Date.today())
        date_from += timedelta(days=25)
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # We have to transform the date in correct format
        new_date_from = fields.Date.today()
        # The product should be saved before the former member
        # former member it
        member = self.env.ref("mozaik_membership.member")
        former_member = self.env.ref("mozaik_membership.former_member")
        created = membership._change_state(
            member, former_member, date_from=new_date_from
        )
        # Due to the date set into parameters, we shouldn't have a new line
        self.assertFalse(created)
        return

    def test_active_vs_date_to(self):
        """
        Test the compatibility between active and date_to field
        """
        membership_obj = self.membership_obj
        price = 0
        reference = str(uuid4())
        instance = self.instance
        partner = self.partner_marc
        product = self.product_subscription
        state = partner.membership_state_id
        date_from = "2015-06-05"
        values = self._get_membership_line_values(
            price=price,
            ref=reference,
            partner=partner,
            product=product,
            date_from=date_from,
            state=state,
            instance=instance,
        )
        membership = membership_obj.create(values)
        # OK: active != bool(date_to)
        self.assertNotEqual(membership.active, bool(membership.date_to))
        # NOK: active=False; date_to=False
        with self.assertRaises(ValidationError):
            membership.active = False
        membership.active = True
        # NOK: active=True; date_to!=False
        with self.assertRaises(ValidationError):
            membership.date_to = date_from
        membership.write(
            {
                "active": False,
                "date_to": date_from,
            }
        )
        # OK: active != bool(date_to)
        self.assertNotEqual(membership.active, bool(membership.date_to))
        return
