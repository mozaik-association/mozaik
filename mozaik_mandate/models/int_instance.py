# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class IntInstance(models.Model):

    _inherit = "int.instance"

    def _get_model_ids(self, model):
        """
        Get all ids for a given model that are linked to an designation
        assembly for the current instance
        :type model: char
        :param model: model is the name of the model to make the search
        :rtype: [integer]
        :rparam: list of ids for the model `model`.
        """
        self.ensure_one()
        assembly_obj = self.env["int.assembly"]
        model_obj = self.env[model]
        domain = [("instance_id", "=", self.id), ("is_designation_assembly", "=", True)]
        assembly_ids = assembly_obj.search(domain).ids
        domain = [
            ("designation_int_assembly_id", "in", assembly_ids),
        ]
        res_ids = model_obj.search(domain).ids
        return res_ids

    def get_model_action(self):
        """
        return an action for a specific model contains into the context
        """
        self.ensure_one()
        context = self.env.context
        action = context.get("action")
        if not action:
            raise Warning(
                _(
                    "A model and an action for this model are required for "
                    "this operation"
                )
            )

        # get model's action to update its domain
        action = self.env["ir.actions.act_window"]._for_xml_id(action)
        model = action["res_model"]
        res_ids = self._get_model_ids(model)
        domain = [("id", "in", res_ids)]
        action["domain"] = domain
        return action

    def _compute_mandate_count(self):
        """
        This method will set the value for
        * sta_mandate_count
        * ext_mandate_count
        * int_mandate_count
        """
        for inst in self:
            inst.ext_mandate_count = len(inst._get_model_ids("ext.mandate"))
            inst.int_mandate_count = len(inst._get_model_ids("int.mandate"))
            inst.sta_mandate_count = len(inst._get_model_ids("sta.mandate"))

    def _get_reference_mandate(self):
        """
        Return the reference mandate associated to an instance
        """
        self.ensure_one()
        if isinstance(self.id, models.NewId):
            return False
        query = """
        SELECT m.id,
        CASE
            WHEN p.address_address_id IS NOT NULL
              AND p.email IS NOT NULL THEN 0
            WHEN p.email IS NOT NULL THEN 1
            WHEN p.address_address_id IS NOT NULL THEN 2
            ELSE 3
        END AS sort
        FROM int_assembly a, int_assembly_category ac, int_mandate m
        LEFT OUTER JOIN res_partner AS p
        ON p.id = m.partner_id
        WHERE a.instance_id = %s
        AND ac.id = a.assembly_category_id
        AND ac.is_secretariat
        AND m.int_assembly_id = a.id
        AND m.active
        AND m.start_date <= current_date
        AND m.end_date IS NULL
        ORDER BY sort, m.start_date
        """
        self._cr.execute(query, (self.id,))
        m_ids = [m_id for m_id, __ in self._cr.fetchall()]
        mandates = self.env["int.mandate"].search([("id", "in", m_ids)])
        # resort
        mandates = {m.id: m for m in mandates}
        mandates = [mandates[mid] for mid in m_ids if mid in mandates]
        return mandates[0] if mandates else False

    @api.depends("assembly_ids")
    def _compute_ref_mandate(self):
        for instance in self:
            instance.ref_mandate_id = instance._get_reference_mandate()

    sta_mandate_count = fields.Integer(
        compute="_compute_mandate_count", string="State Mandates"
    )
    ext_mandate_count = fields.Integer(
        compute="_compute_mandate_count", string="External Mandates"
    )
    int_mandate_count = fields.Integer(
        compute="_compute_mandate_count", string="Internal Mandates"
    )
    ref_mandate_id = fields.Many2one(
        "int.mandate",
        string="Reference Mandate",
        readonly=True,
        compute="_compute_ref_mandate",
    )
