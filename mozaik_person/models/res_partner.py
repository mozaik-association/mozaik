# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.osv.expression import OR

from odoo.addons.mozaik_tools.tools import format_value


class ResPartner(models.Model):

    _name = "res.partner"
    _inherit = ["abstract.duplicate", "res.partner"]

    _allowed_inactive_link_models = ["res.partner", "co.residency"]
    _inactive_cascade = True

    _discriminant_fields = {
        "name": {
            "field_duplicate": "is_name_duplicate_detected",
            "field_allowed": "is_name_duplicate_allowed",
            "reset_allowed": True,
        },
        "email": {
            "field_duplicate": "is_email_duplicate_detected",
            "field_allowed": "is_email_duplicate_allowed",
            "reset_allowed": True,
        },
        "phone": {
            "field_duplicate": "is_phone_duplicate_detected",
            "field_allowed": "is_phone_duplicate_allowed",
            "reset_allowed": True,
        },
        "mobile": {
            "field_duplicate": "is_mobile_duplicate_detected",
            "field_allowed": "is_mobile_duplicate_allowed",
            "reset_allowed": True,
        },
        "address_address_id": {
            "field_duplicate": "is_address_duplicate_detected",
            "field_allowed": "is_address_duplicate_allowed_compute",
            "reset_allowed": False,
        },
    }
    _trigger_fields = [
        "active",
        "name",
        "lastname",
        "firstname",
        "birthdate_date",
        "email",
        "phone",
        "mobile",
        "address_address_id",
        "co_residency_id",
    ]
    _undo_redirect_action = "contacts.action_contacts"
    _order = "select_name"
    _unicity_keys = "N/A"

    is_name_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_name_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
    )

    is_email_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_email_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
    )

    is_mobile_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_mobile_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
    )

    is_phone_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_phone_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_address_duplicate_detected = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_address_duplicate_allowed = fields.Boolean(
        readonly=True,
        copy=False,
    )
    is_address_duplicate_allowed_compute = fields.Boolean(
        readonly=True,
        copy=False,
        compute="_compute_is_address_duplicate_allowed",
        inverse="_inverse_is_address_duplicate_allowed",
        store=True,
    )

    identifier = fields.Char(
        "Number",
        index=True,
        copy=False,
        default=False,
        group_operator="min",
    )
    acronym = fields.Char(
        tracking=True,
    )
    select_name = fields.Char(
        compute="_compute_names",
        store=True,
        index=True,
    )
    technical_name = fields.Char(
        compute="_compute_names",
        store=True,
        index=True,
    )
    printable_name = fields.Char(
        compute="_compute_names",
        store=True,
        index=True,
    )

    # complete existing fields
    firstname = fields.Char(
        tracking=True,
    )
    lastname = fields.Char(
        tracking=True,
    )
    usual_firstname = fields.Char(
        tracking=True,
    )
    usual_lastname = fields.Char(
        tracking=True,
    )

    # When the field isn't redefined, Odoo will sometimes not see the
    # definition of display_name in the base addon,
    # so it's the default one (magic field) which will be used,
    # and this field is not store. The result can change on every restart,
    # and this will lead on possible blank display_name for certain partner.
    # (partner which was created when store=False will have empty value when
    # store=True)
    # Redefining it here somehow forces odoo to notice the field in base.
    display_name = fields.Char()

    @api.depends(
        "is_company",
        "name",
        "parent_id.name",
        "type",
        "company_name",
        "identifier",
        "select_name",
    )
    def _compute_display_name(self):
        return super()._compute_display_name()

    @api.depends("co_residency_id", "is_address_duplicate_allowed")
    def _compute_is_address_duplicate_allowed(self):
        for partner in self:
            partner.is_address_duplicate_allowed_compute = (
                partner.is_address_duplicate_allowed or partner.co_residency_id
            )

    def _inverse_is_address_duplicate_allowed(self):
        for partner in self:
            partner.is_address_duplicate_allowed = (
                partner.is_address_duplicate_allowed_compute
            )
            if not partner.is_address_duplicate_allowed_compute:
                partner.co_residency_id = False

    @api.depends(
        "is_company",
        "acronym",
        "identifier",
        "name",
        "usual_name",
        "firstname",
        "lastname",
        "usual_firstname",
        "usual_lastname",
    )
    def _compute_names(self):
        """
        Compute derived names from firstname and lastname
        """
        for partner in self:
            if partner.is_company:
                s_name = p_name = partner.name
                if partner.acronym:
                    s_name = "%s (%s)" % (partner.name, partner.acronym)
            else:
                s_name = partner.usual_name
                if s_name != partner.name:
                    s_name = "%s (%s)" % (s_name, partner.name)
                names = partner._get_names(usual=True, reverse=True)
                p_name = partner._get_computed_name(names[0], names[1])

            partner.select_name = s_name
            partner.technical_name = format_value(s_name, remove_blanks=True)
            partner.printable_name = p_name

    @api.constrains("identifier")
    def _check_identifier(self):
        """
        Check if identifier is unique
        """
        partners = self.filtered(lambda s: s.identifier)
        identifiers = partners.mapped("identifier")
        if not identifiers:
            return
        other = (
            self.env["res.partner"].sudo().search([("identifier", "in", identifiers)])
        )
        for partner in partners:
            p = other.filtered(
                lambda s, p=partner: s != p and s.identifier == p.identifier
            )
            if p:
                raise exceptions.ValidationError(
                    _("Identifier %s is already assigned") % partner.identifier
                )

    @api.model
    def _get_duplicates(self, value, discriminant_field):
        """
        Get duplicates
        * If discriminant_field is address and if address is not complete
        -> partial address must not be a discriminant field. Return no duplicate
        * If one of these duplicates has no ``birthdate_date`` return all
          duplicates
        * Otherwise return duplicates with the same ``birthdate_date``
          and reset all others
        :param value: discriminant field values (dict with all discriminant fields)
        :return: self recordset
        """
        duplicates = super()._get_duplicates(value, discriminant_field)
        if discriminant_field == "address_address_id":
            address = self.env["address.address"].browse(value[discriminant_field])
            if not address.has_street:
                values_write = self._get_fields_to_update_duplicate(
                    "reset", "address_address_id"
                )
                duplicates.with_context(escape_detection=True).write(values_write)
                return self.browse()
        if duplicates.filtered(lambda s: not s.birthdate_date):
            return duplicates

        detected_duplicates = duplicates
        if duplicates and discriminant_field == "name":
            detected_duplicates = self.browse()
            # group duplicates by birth date
            dates = duplicates.mapped("birthdate_date")
            duplicates_by_date = {d: self.browse() for d in dates}
            for duplicate in duplicates:
                duplicates_by_date[duplicate.birthdate_date] |= duplicate
            # all groups of size > 1 are real duplicates
            # all groups of size = 1 are false duplicates
            false_duplicates = self.browse()
            for grp in duplicates_by_date.values():
                if len(grp) > 1:
                    detected_duplicates |= grp
                else:
                    false_duplicates |= grp
            # reset false duplicates
            false_duplicates = false_duplicates.filtered(
                lambda s: s.is_name_duplicate_allowed or s.is_name_duplicate_detected
            )
            if false_duplicates:
                values_write = self._get_fields_to_update_duplicate("reset", "name")
                false_duplicates.with_context(escape_detection=True).write(values_write)
        return detected_duplicates

    def write(self, vals):
        if vals.get("co_residency_id"):
            vals["is_address_duplicate_detected"] = False
        return super().write(vals)

    def name_get(self):
        """
        Add identifier to name_get result
        """
        result = res = super().name_get()
        if not any(
            [
                self._context.get("show_address_only"),
                self._context.get("show_address"),
                self._context.get("show_email"),
            ]
        ):
            p_dict = {p.id: p for p in self}
            result = []
            for rec in res:
                identifier = p_dict[rec[0]].identifier
                if identifier:
                    result.append(
                        (rec[0], "%s-%s" % (identifier, p_dict[rec[0]].select_name))
                    )
                else:
                    result.append((rec[0], p_dict[rec[0]].select_name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            op = (
                operator
                if operator
                in [
                    "like",
                    "ilike",
                    "=",
                ]
                else "ilike"
            )
            ident = int(name) if name.isdigit() else -1
            domain = [
                "|",
                "|",
                ("select_name", op, name),
                ("technical_name", op, name),
                ("identifier", "=", ident),
            ]
        partners = self.search(domain + args, limit=limit)
        return partners.name_get()

    @api.model
    def create(self, vals):
        """
        Add an identifier from a sequence if any
        """
        if vals.get("is_assembly"):
            vals.pop("identifier")
        if not vals.get("is_assembly") and not vals.get("identifier"):
            vals["identifier"] = self.env["ir.sequence"].next_by_code("res.partner")

        res = super().create(vals)
        return res

    def _create_user(self, login, role_id):
        """
        Create a user from an existing partner
        :param login: char
        :param role_id: recordset
        :raise: if partner is already a user or is a company or is inactive
        :return: the user
        """
        self.ensure_one()

        if self.user_ids:
            raise exceptions.UserError(_("%s is already a user!") % self.display_name)

        if self.is_company and not self.is_assembly:
            raise exceptions.UserError(
                _("%s cannot be a company to become a user!") % self.display_name
            )

        if not self.active:
            raise exceptions.UserError(
                _("%s must be active to become a user!") % self.display_name
            )

        vals = {"role_line_ids": [(0, 0, {"role_id": role_id.id})]} if role_id else {}
        vals.update(
            {
                "partner_id": self.id,
                "login": login,
            }
        )

        user = self.env["res.users"].with_context(no_reset_password=True).create(vals)

        return user

    @api.model
    def _update_identifier_sequence(self):
        """
        Update next value (after data migration) of identifier sequence
        """
        self.env.cr.execute(
            """
            SELECT MAX(identifier::numeric) + 1
            FROM res_partner"""
        )
        next_value = self.env.cr.fetchone()[0] or 0
        seq = self.env.ref("mozaik_person.res_partner_identifier_sequence")
        seq.number_next = int(next_value)

    def show_duplicates(self):
        self.ensure_one()
        duplicate_form = (
            self.sudo().env.ref("mozaik_person.res_partner_duplicate_action").read()[0]
        )
        domain = []
        if self.name:
            domain.append([("name", "ilike", self.name)])
        if self.email:
            domain.append([("email", "ilike", self.email)])
        if self.phone:
            domain.append([("phone", "ilike", self.phone)])
        if self.mobile:
            domain.append([("mobile", "ilike", self.mobile)])
        if self.address_address_id:
            domain.append([("address_address_id", "=", self.address_address_id.id)])
        duplicate_form["domain"] = OR(domain)
        return duplicate_form
