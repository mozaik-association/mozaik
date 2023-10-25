# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.survey.tests.common import SurveyCase


class TestSurveyInvite(SurveyCase):
    def setUp(self):
        super().setUp()
        self.partner_model = self.env["res.partner"]
        self.dist_list_model = self.env["distribution.list"]
        self.dist_list_line_model = self.env["distribution.list.line"]
        self.dist_list_line_tmpl_model = self.env["distribution.list.line.template"]
        self.wizard_model = self.env["survey.invite"]

        self.partner_1 = self.partner_model.create(
            {"name": "Test Distribution 1", "email": "test1@test.com"}
        )
        self.partner_2 = self.partner_model.create(
            {"name": "Test Distribution 2", "email": "test2@test.com"}
        )

        distribution_list_template = self.dist_list_line_tmpl_model.create(
            {
                "name": "Test distribution list",
                "domain": "[('name', 'ilike', 'Test Distribution')]",
                "src_model_id": self.env.ref("base.model_res_partner").id,
            }
        )
        dist_list_line_values = {
            "distribution_list_line_tmpl_id": distribution_list_template.id,
            "exclude": False,
            "bridge_field_id": self.env.ref("base.field_res_partner__id").id,
        }
        self.distribution_list = self.dist_list_model.create(
            {
                "name": "Test survey",
                "dst_model_id": self.env.ref("base.model_res_partner").id,
                "to_include_distribution_list_line_ids": [
                    (0, False, dist_list_line_values),
                ],
            }
        )

    def test_survey_invite_with_distribution_list(self):
        """
        Data:
            - a survey
            - 2 partners
            - a distribution list that targets those 2 partners
        Test case:
            - open the survey.invite wizard with the survey and set the distribution_list
            - unset the distribution list
        Expected result:
            - the partners field in the wizard is set and unset correctly
        """
        wizard = self.wizard_model.create({"survey_id": self.survey.id})

        self.assertFalse(wizard.partner_ids)
        wizard.distribution_list_id = self.distribution_list
        self.assertEqual(len(wizard.partner_ids), 2)
        self.assertTrue(self.partner_1 in wizard.partner_ids)
        self.assertTrue(self.partner_2 in wizard.partner_ids)

        wizard.distribution_list_id = False
        self.assertFalse(wizard.partner_ids)
