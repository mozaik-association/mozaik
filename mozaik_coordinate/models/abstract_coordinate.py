# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class AbstractCoordinate(models.AbstractModel):
    _name = "abstract.coordinate"
    _inherit = ["abstract.duplicate"]
    _description = "Abstract Coordinate"
    _order = "expire_date, is_main desc, coordinate_type"

    _discriminant_field = None
    _log_access = True

    partner_id = fields.Many2one(
        "res.partner",
        "Contact",
        readonly=True,
        required=True,
        index=True,
        auto_join=True,
    )
    coordinate_category_id = fields.Many2one(
        "coordinate.category",
        string="Coordinate Category",
        tracking=True,
        index=True,
    )
    coordinate_type = fields.Selection(
        [
            ("n/a", "N/A"),
        ],
        default="n/a",
    )
    is_main = fields.Boolean(
        readonly=True,
        default=False,
        index=True,
    )
    unauthorized = fields.Boolean(
        default=False,
        tracking=True,
    )
    vip = fields.Boolean(
        "VIP",
        default=False,
        tracking=True,
    )
    failure_counter = fields.Integer(
        "Failures Counter",
        default=0,
        copy=False,
        tracking=True,
    )
    failure_description = fields.Text(
        "Last Failure Description",
        copy=False,
        tracking=True,
    )
    failure_date = fields.Datetime(
        "Last Failure Date",
        copy=False,
        tracking=True,
    )

    @api.model
    def _validate_vals(self, values):
        """
        Depending on the partner_id and coordinate_type defined into the
        given values dict, update it to set the "is_main" key to True
        if no others results are found
        :param values: dict
        :return: bool
        """
        partner_id = values.get("partner_id")
        coordinate_type = values.get("coordinate_type")
        domain = self._get_target_domain(partner_id, coordinate_type)
        coordinates = self.sudo().search_count(domain)
        if not coordinates:
            values.update(
                {
                    "is_main": True,
                }
            )

    @api.constrains("partner_id", "is_main", "active", "coordinate_type")
    def _check_one_main_coordinate(self, for_unlink=False):
        """
        Check if associated partner has exactly one main coordinate
        for a given coordinate type
        :param for_unlink: bool
        """
        if self.env.context.get("no_check_main_coordinate"):
            return
        coordinates = self_sudo = self.sudo()
        if for_unlink:
            coordinates = coordinates.filtered(lambda c: c.is_main)
        partners = coordinates.mapped("partner_id")
        coordinate_types = coordinates.mapped("coordinate_type")
        all_other_coordinates = self_sudo.search(
            [
                ("partner_id", "in", partners.ids),
                ("coordinate_type", "in", coordinate_types),
            ]
        )
        for coordinate in coordinates:
            other_coordinates = all_other_coordinates.filtered(
                lambda s, c=coordinate: s.partner_id == c.partner_id
                and s.coordinate_type == c.coordinate_type
            )
            if (
                for_unlink
                and len(other_coordinates) > 1
                and coordinate.is_main
            ):
                raise exceptions.ValidationError(
                    _(
                        "Exactly one main coordinate must exist for a "
                        "given partner"
                    )
                )
            if not other_coordinates:
                continue
            if len(other_coordinates.filtered(lambda x: x.is_main)) != 1:
                raise exceptions.ValidationError(
                    _(
                        "Exactly one main coordinate must exist for a "
                        "given partner"
                    )
                )

    def copy(self, default=None):
        """
        Inherit some default values
        :param default: dict
        :return: self recordset
        """
        self.ensure_one()
        if self.active:
            raise exceptions.UserError(
                _("An active coordinate cannot be duplicated!")
            )
        return super().copy(default=default)

    def name_get(self):
        """
        Update the name_get depending on the discriminant value and
        the context
        :return: list of tuple (int, str)
        """
        result = []
        is_notification = self.env.context.get("is_notification")
        if is_notification:
            for record in self:
                display_name = "%s: %s" % (
                    record.partner_id.display_name,
                    record._get_discriminant_value("display_name"),
                )
                result.append((record.id, display_name))
        else:
            result = super().name_get()
        return result

    @api.model
    def _get_default_coordinate_type(self, values):
        """
        Get the default coordinate type.
        Useful for inherit
        :param values: dict
        :return: str
        """
        return "n/a"

    @api.model
    def create(self, vals):
        """
        When 'is_main' is true the coordinate has to become
        the main coordinate for its associated partner.
        Automatically add the partner as follower of its coordinate

        **Note**
        If new coordinate is main and another main coordinate found into
        the database then the other(s) will not be main anymore
        :param vals: dict
        :return: self recordset
        """
        coordinate_type = vals.get("coordinate_type")
        partner_id = vals.get("partner_id")
        if "coordinate_type" not in vals:
            coordinate_type = self._get_default_coordinate_type(vals)
            vals.update(
                {
                    "coordinate_type": coordinate_type,
                }
            )
        self._validate_vals(vals)
        if vals.get("is_main"):
            domain_other_active_main = self._get_target_domain(
                partner_id, coordinate_type
            )
            invalidate = self.env.context.get("invalidate")
            mode = "deactivate" if invalidate else "secondary"
            validate_fields = self._get_fields_to_update(mode)
            self._search_and_update(domain_other_active_main, validate_fields)
        return super().create(vals)

    def unlink(self):
        """
        During unlink, check if a one main coordinate still available
        :return: bool
        """
        main_coordinates = self.filtered(lambda s: s.is_main)
        unlink_first = self - main_coordinates
        result = True
        if unlink_first:
            result = super(AbstractCoordinate, unlink_first).unlink()
        if main_coordinates:
            main_coordinates._check_one_main_coordinate(for_unlink=True)
            result = super(AbstractCoordinate, main_coordinates).unlink()
        return result

    def button_reset_counter(self):
        """
        Reset the failure counter
        """
        self.write({"failure_counter": 0})

    @api.model
    def _search_and_update(self, target_domain, fields_to_update):
        """
        1) Search with self on ``target_domain``
        2) Update self with ``fields_to_update``
        :param target_domain: list of tuple (domain)
        :param fields_to_update: dict
        :return: bool
        """
        results = self.search(target_domain)
        if results:
            results.with_context(no_check_main_coordinate=True).write(
                fields_to_update
            )

    @api.model
    def _get_target_domain(self, coordinate_type):
        """
        Get a domain to look for the target
        :param coordinate_type: str
        :return: list of tuple (domain)
        """
        return [
            ("coordinate_type", "=", coordinate_type),
            ("is_main", "=", True),
        ]

    @api.model
    def _get_fields_to_update(self, mode):
        """
        Depending on the mode, update the dict to update fields
        :param mode: str
        :return: dict
        """
        result = super()._get_fields_to_update(mode)
        if mode == "main":
            result.update(
                {
                    "is_main": True,
                }
            )
        if mode == "secondary":
            result.update(
                {
                    "is_main": False,
                }
            )
        return result

    def ensure_one_main_coordinate(self, invalidate=False, vals=False):
        """
        Ensure that at least 1 main coordinate will remain after an action
        :param invalidate: bool
        :param vals: dict
        :return:
        """
        limit = 1 if not invalidate else False
        rejected = self.env[self[0]._name].browse()
        for coordinate in self:
            domain = [
                ("partner_id", "=", coordinate.partner_id.id),
                ("coordinate_type", "=", coordinate.coordinate_type),
            ]
            if invalidate:
                domain.append(("id", "not in", self.ids))
            else:
                domain.append(("id", "!=", coordinate.id))
            coords = self.sudo().search(domain, limit=limit)
            if coordinate.is_main and len(coords) == 1:
                coordinate_value = coords._get_discriminant_value()
                coordinate_ctx = coordinate.with_context(invalidate=invalidate)
                coordinate_ctx._change_main_coordinate(
                    coordinate.partner_id, coordinate_value
                )
                if vals:
                    coordinate_ctx.write(vals)
            else:
                rejected |= coordinate
        return rejected

    def action_invalidate(self, vals=None):
        rejected_ids = self.ensure_one_main_coordinate(invalidate=True)
        if rejected_ids:
            return super(AbstractCoordinate, rejected_ids).action_invalidate(
                vals=vals
            )
        return True
