# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestHrEmployee(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.be = cls.env.ref("base.be")
        cls.address1 = cls.env["res.partner"].create(
            {
                "name": "Adresse Liège",
                "street": "Rue du puits",
                "zip": "4000",
                "city": "Liège",
                "country_id": cls.be.id,
            }
        )
        cls.address2 = cls.env["res.partner"].create(
            {
                "name": "Adresse Namur",
                "street": "Rue du Moulin",
                "zip": "5000",
                "city": "Namur",
                "country_id": cls.be.id,
            }
        )
        cls.env.company.partner_id.write(
            {
                "street": "Rue de la Foret",
                "zip": "1000",
                "city": "Bruxelles",
                "country_id": cls.be.id,
            }
        )

    def test_setup_initial_department(self):
        """
        Create a new department -> Address is address of the company
        """
        dept = self.env["hr.department"].create({"name": "Main department"})
        self.assertEqual(dept.address_id, self.env.company.partner_id)

    def test_children_department(self):
        dept = self.env["hr.department"].create({"name": "Main department"})
        dept.address_id = self.address1
        child_dept = self.env["hr.department"].create(
            {"name": "Child department", "parent_id": dept.id}
        )
        self.assertEqual(child_dept.address_id, self.address1)

    def test_set_department_on_employee(self):
        dept = self.env["hr.department"].create(
            {"name": "Main department", "address_id": self.address1.id}
        )
        employee = self.env["hr.employee"].create(
            {"name": "Test employee", "department_id": dept.id}
        )
        self.assertEqual(employee.address_id, self.address1)

    def test_change_address_main_department_propagate(self):
        dept = self.env["hr.department"].create({"name": "Main department"})
        dept.address_id = self.address1
        child_dept = self.env["hr.department"].create(
            {"name": "Child department", "parent_id": dept.id}
        )
        employee = self.env["hr.employee"].create(
            {"name": "Test employee", "department_id": dept.id}
        )
        self.assertEqual(child_dept.address_id, self.address1)
        self.assertEqual(employee.address_id, self.address1)
        dept.address_id = self.address2
        self.assertEqual(child_dept.address_id, self.address2)
        self.assertEqual(employee.address_id, self.address2)
