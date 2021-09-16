# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class AbstractDuplicate(models.AbstractModel):
    _name = "abstract.duplicate"
    _inherit = ["mozaik.abstract.model"]
    _description = "Abstract Duplicate Model"

    _discriminant_fields = {}
    # dict of:
    #   key: model field
    #   value: dict
    #     reset_allowed: boolean
    #     field_allowed: str
    #     field_duplicate: str

    _trigger_fields = []
    _undo_redirect_action = None

    is_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
        tracking=True,
        store=True,
        compute="_compute_is_duplicate_detected",
    )

    @api.model
    def _is_duplicate_detected_depends_fields(self):
        res = []
        for field_data in self._discriminant_fields.values():
            res.append(field_data["field_duplicate"])
        return res

    @api.depends(_is_duplicate_detected_depends_fields)
    def _compute_is_duplicate_detected(self):
        for o in self:
            duplicate_detected = False
            for field_data in self._discriminant_fields.values():
                if o[field_data["field_duplicate"]]:
                    duplicate_detected = True
                    break
            o.is_duplicate_detected = duplicate_detected

    def _get_discriminant_values(self):
        """
        Get the value of the discriminant field
        :param force_field: str
        :return: str, int, float, bool
        """
        self.ensure_one()
        vals = {}
        for discriminant_field in self._discriminant_fields:
            value = self[discriminant_field]
            if isinstance(self._fields[discriminant_field], fields.Many2one):
                value = value.id
            if value:
                vals[discriminant_field] = value
        return vals

    @api.model
    def create(self, vals):
        """
        Override create method to detect and repair duplicates.
        :param vals: dict
        :return: self recordset
        """
        result = super().create(vals)
        if result:
            result = result.sudo()
            value = result._get_discriminant_values()
            self.sudo()._detect_and_repair_duplicate(value)
        return result

    def write(self, vals):
        """
        Override write method to detect and repair duplicates.
        :param vals: dict
        :return: bool
        """
        trigger_fields = self._get_trigger_fields(vals.keys())
        detect = self and trigger_fields and not self._context.get("escape_detection")
        if detect:
            self_sudo = self.sudo()
            values = [d._get_discriminant_values() for d in self_sudo]
        result = super().write(vals)
        if detect:
            values += [d._get_discriminant_values() for d in self_sudo]
            self_sudo._detect_and_repair_duplicate(values)
        return result

    def _get_trigger_fields(self, fields_list):
        """
        Get a list of fields who are into _trigger_fields and into given
        fields_list parameter (intersection).
        :param fields_list: list of str
        :return:
        """
        trigger_fields = self._trigger_fields or list(self._discriminant_fields.keys())
        for v in self._discriminant_fields.values():
            field_allowed = v.get("field_allowed")
            if field_allowed:
                trigger_fields.append(field_allowed)
            field_duplicate = v.get("field_duplicate")
            if field_duplicate:
                trigger_fields.append(field_duplicate)
        return list(set(trigger_fields).intersection(fields_list))

    def unlink(self):
        """
        Override unlink method to detect and repair duplicates.
        :return: bool
        """
        self_sudo = self.sudo()
        values = False
        if self:
            values = [d._get_discriminant_values() for d in self_sudo]
        result = super().unlink()
        if values:
            self_sudo._detect_and_repair_duplicate(values)
        return result

    def button_undo_allow_duplicate(self):
        """
        Undo the effect of the "Allow duplicate" wizard.
        All allowed duplicates will be reset
        (see _detect_and_repair_duplicate).
        :return: dict
        """
        self.write(
            {
                self._discriminant_fields[self.env.context["discriminant_field"]][
                    "field_allowed"
                ]: False
            }
        )

        if len(self) != 1:
            return True

        # Reload the tree with all duplicates
        value = self._get_discriminant_values()
        action = self.env.ref(self._undo_redirect_action).read()[0]
        # force the tree view
        action["view_mode"] = "tree," + action["view_mode"].replace("tree,", "")
        action.pop("search_view", False)
        context = safe_eval(action["context"])
        for discriminant_field in self._discriminant_fields:
            if value.get(discriminant_field):
                context["search_default_%s" % discriminant_field] = value[
                    discriminant_field
                ]
        action.update(
            {
                "context": context,
            }
        )
        return action

    @api.model
    def _get_fields_to_update_duplicate(self, mode, field):
        """
        Depending on a mode, builds a dictionary allowing to update duplicate
        fields
        :param mode: str
        :return: dict
        """
        result = {}
        if mode in ["reset", "deactivate"]:
            result.update(
                {
                    self._discriminant_fields[field]["field_duplicate"]: False,
                    self._discriminant_fields[field]["field_allowed"]: False,
                }
            )
        elif mode == "duplicate":
            result.update(
                {
                    self._discriminant_fields[field]["field_duplicate"]: True,
                    self._discriminant_fields[field]["field_allowed"]: False,
                }
            )
        elif mode == "allow":
            result.update(
                {
                    self._discriminant_fields[field]["field_duplicate"]: False,
                    self._discriminant_fields[field]["field_allowed"]: True,
                }
            )
        return result

    @api.model
    def _get_fields_to_update(self, mode):
        """
        Depending on a mode, builds a dictionary allowing to update duplicate
        fields
        :param mode: str
        :return: dict
        """
        result = super()._get_fields_to_update(mode)
        if mode in ["reset", "deactivate"]:
            for key in self._discriminant_fields:
                result.update(
                    {
                        self._discriminant_fields[key]["field_duplicate"]: False,
                        self._discriminant_fields[key]["field_allowed"]: False,
                    }
                )
        return result

    @api.model
    def _get_duplicates(self, value, discriminant_field):
        """
        Get duplicates
        :param value: dict of field: value
        :return: self recordset
        """
        domain = [(discriminant_field, "=", value[discriminant_field])]
        return self.search(domain)

    @api.model
    def _detect_and_repair_duplicate(self, values, field_model=None, field_id=None):
        """
        Detect automatically duplicates (setting the is_duplicate_detected
        flag)
        Repair orphan allowed or detected duplicate (resetting the
        corresponding flag)
        field_model and field_id must be both set to be used
        :param values: list
        :param field_model: name of the field to get the model
        :param field_id: name of the field to read to get the id
        :return:
        """
        if not isinstance(values, list):
            values = [values]
        for value in values:
            for discriminant_field in value:
                duplicates = self._get_duplicates(value, discriminant_field)
                values_write = {}
                if len(duplicates) > 1:
                    val = {}
                    field_value = self._discriminant_fields[discriminant_field]

                    nb_duplicates = len(
                        duplicates.filtered(
                            lambda d: not d[field_value["field_duplicate"]]
                            and d[field_value["field_allowed"]]
                        )
                    )
                    if nb_duplicates == 1 or self._discriminant_fields[
                        discriminant_field
                    ].get("reset_allowed", False):
                        val.update(
                            {
                                field_value["field_allowed"]: False,
                            }
                        )
                    nb_duplicates = len(
                        duplicates.filtered(
                            lambda d: not d[field_value["field_duplicate"]]
                            and not d[field_value["field_allowed"]]
                        )
                    )
                    if nb_duplicates >= 1:
                        values_write.update(
                            self._get_fields_to_update_duplicate(
                                "duplicate", discriminant_field
                            )
                        )
                elif len(duplicates) == 1:
                    field_value = self._discriminant_fields[discriminant_field]
                    if (
                        duplicates[field_value["field_allowed"]]
                        or duplicates[field_value["field_duplicate"]]
                    ):
                        values_write.update(
                            self._get_fields_to_update_duplicate(
                                "reset", discriminant_field
                            )
                        )

                if values_write:
                    if field_model and field_id:
                        for duplicate in duplicates:
                            record = self.env[duplicate[field_model]].browse(
                                duplicate[field_id]
                            )
                            # super write method must be called here to avoid to cycle
                            super(AbstractDuplicate, record).write(values_write)
                    else:
                        duplicates.write(values_write)
        return True
