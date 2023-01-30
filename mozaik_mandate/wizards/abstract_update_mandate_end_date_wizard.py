# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AbstractUpdateMandateEndDateWizard(models.TransientModel):

    _name = "abstract.update.mandate.end.date.wizard"
    _description = "Abstract Update Mandate End Date Wizard"

    mandate_end_date = fields.Date()
    mandate_deadline_date = fields.Date()
    # We must pass active_test=False in context otherwise default_get
    # will not save archived mandates in the wizard
    mandate_ids = fields.Many2many(
        comodel_name="abstract.mandate",
        string="Mandates",
        readonly=True,
        context={"active_test": False},
    )
    message = fields.Char(readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        context = self.env.context

        mode = context.get("mode", "end_date")

        model = context.get("active_model", False)
        if not model:
            return res

        mandate_ids = (
            context.get("active_ids")
            or (context.get("active_id") and [context.get("active_id")])
            or []
        )

        mandates = self.env[model].browse(mandate_ids)
        res["mandate_ids"] = [(6, 0, mandate_ids)]

        if mode == "end_date":
            res["mandate_end_date"] = fields.Date.today()

            if mandates.filtered("active"):
                res["message"] = _(
                    "Some mandates will be invalidated by setting their end date!"
                )
        elif mode == "reactivate":
            res["message"] = ""
            if mandates.filtered("active"):
                res["message"] += _("Some of the selected mandates are already active!")
            if mandates.filtered(lambda m: not m.mandate_category_id.active):
                res["message"] += _(
                    "Some of the mandate categories are no longer active!"
                )
            if mandates.filtered(
                lambda m: m.designation_int_assembly_id
                and not m.designation_int_assembly_id.active
            ):
                res["message"] += _(
                    "Some of the designation assemblies are no longer active!"
                )
            if mandates.filtered(lambda m: not m.partner_id.active):
                res["message"] += _("Some of the representatives are no longer active!")
            if res["message"] == "":
                res["message"] = False
        return res

    def set_mandate_end_date(self):
        self.ensure_one()
        if self.mandate_end_date > fields.Date.today():
            raise ValidationError(_("End date must be lower or equal than today!"))
        if any(
            self.mandate_end_date > mandate.deadline_date
            for mandate in self.mandate_ids
        ):
            raise ValidationError(
                _(
                    "End date must be lower or equal than deadline date on all selected"
                    "mandates!"
                )
            )
        if any(
            mandate.start_date > self.mandate_end_date for mandate in self.mandate_ids
        ):
            raise ValidationError(
                _(
                    "End date must be greater or equal than start date on all selected"
                    "mandates!"
                )
            )
        vals = {"end_date": self.mandate_end_date}
        active_mandates = self.mandate_ids.filtered("active")
        active_mandates.action_invalidate(vals=vals)
        (self.mandate_ids - active_mandates).write(vals=vals)

    def reactivate_mandate(self):
        self.ensure_one()
        if self.mandate_deadline_date <= fields.Date.today():
            raise ValidationError(_("New deadline date must be greater than today !"))

        vals = {
            "deadline_date": self.mandate_deadline_date,
            "end_date": False,
        }
        self.mandate_ids.action_revalidate(vals=vals)
