# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from collections import OrderedDict
from datetime import date, datetime
from operator import attrgetter
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import first
from odoo.tools import safe_eval
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.mozaik_tools.tools import (
    check_and_format_number,
    check_email,
    format_email,
    get_age,
)

_logger = logging.getLogger(__name__)

MEMBERSHIP_AVAILABLE_STATES = [
    ("draft", "Draft"),
    ("confirm", "Confirmed"),
    ("validate", "Done"),
    ("cancel", "Cancelled"),
]

EMPTY_ADDRESS = "0#0#0#0#0#0#0#0"
MEMBERSHIP_REQUEST_TYPE = [
    ("m", "Member"),
    ("s", "Supporter"),
]
MR_REQUIRED_AGE_KEY = "mr_required_age"

ERRORS_DICT = {
    "exists_on_other_mr_and_no_partner_set": _(
        "You didn't set a partner and the reference"
        " already exists on another membership request."
    ),
    "ref_on_mr_with_other_partner": _(
        "The reference already exists on a "
        "membership request linked to another partner."
    ),
    "ref_on_res_partner_or_inactive_line": _(
        "The reference already exists on another partner, "
        "or the reference corresponds to an inactive membership line."
    ),
}

VOLUNTARY_FIELDS = [
    "local_voluntary",
    "regional_voluntary",
    "national_voluntary",
    "local_only",
]


def partner_add_values(mr, partner_values):
    if not mr.is_company:
        partner_values["firstname"] = mr.firstname
        if mr.gender:
            partner_values["gender"] = mr.gender
        if mr.birthdate_date:
            partner_values["birthdate_date"] = mr.birthdate_date

    if mr.nationality_id:
        partner_values["nationality_id"] = mr.nationality_id.id


class MembershipRequest(models.Model):

    _name = "membership.request"
    _inherit = ["mozaik.abstract.model", "mozaik.lowered.email.mixin"]
    _description = "Membership Request"
    _inactive_cascade = True
    _terms = ["interest_ids", "competency_ids"]
    _order = "id desc"
    _unicity_keys = "N/A"

    identifier = fields.Char(related="partner_id.identifier", string="Identifier")
    is_company = fields.Boolean("Is a Company", default=False)
    lastname = fields.Char("Name", required=True, tracking=True)
    firstname = fields.Char("Firstname", tracking=True)

    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
        index=True,
        tracking=True,
    )
    email = fields.Char("Email", tracking=True)
    phone = fields.Char("Phone", tracking=True)
    mobile = fields.Char("Mobile", tracking=True)
    day = fields.Char("Day")
    month = fields.Char("Month")
    year = fields.Char("Year")
    birthdate_date = fields.Date("Birth Date", tracking=True)

    # request and states
    request_type = fields.Selection(
        selection=MEMBERSHIP_REQUEST_TYPE, string="Request Type", tracking=True
    )
    membership_state_id = fields.Many2one(
        comodel_name="membership.state", string="Current State"
    )
    result_type_id = fields.Many2one(
        comodel_name="membership.state", string="Expected State"
    )
    is_update = fields.Boolean(string="Is Update", default=False)
    state = fields.Selection(
        selection=MEMBERSHIP_AVAILABLE_STATES,
        string="State",
        tracking=True,
        default="draft",
    )

    # address
    country_id = fields.Many2one(
        comodel_name="res.country", string="Country", index=True, tracking=True
    )
    enforce_cities = fields.Boolean(related="country_id.enforce_cities", readonly=True)

    city_id = fields.Many2one(comodel_name="res.city", string="City", tracking=True)
    local_zip = fields.Char(related="city_id.zipcode", string="Local Zip", store=True)
    zip_man = fields.Char(string="Zip", tracking=True)

    city_man = fields.Char(string="City (Manual)", tracking=True)

    address_local_street_id = fields.Many2one(
        comodel_name="address.local.street",
        string="Reference Street",
        tracking=True,
    )
    street_man = fields.Char(string="Street", tracking=True)
    street2 = fields.Char(string="Street2", tracking=True)

    number = fields.Char(string="Number", tracking=True)
    box = fields.Char(string="Box", tracking=True)
    sequence = fields.Integer(string="Sequence", tracking=True, group_operator="min")

    technical_name = fields.Char(string="Technical Name")

    # indexes
    interest_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="membership_request_interests_rel",
        column1="membership_id",
        column2="thesaurus_term_id",
        string="Interests",
    )
    competency_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="membership_request_competence_rel",
        column1="membership_id",
        column2="thesaurus_term_id",
        string="Competencies",
    )

    note = fields.Text("Notes")

    # references
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        domain="[('membership_state_id', '!=', False)]",
    )

    int_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Internal Instance (real)",
    )
    int_instance_ids_readonly = fields.Many2many(
        related="int_instance_ids",
        string="Internal Instance",
    )
    force_int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal Instance (to Force)",
        tracking=True,
    )

    address_id = fields.Many2one(comodel_name="address.address", string="Address")
    change_ids = fields.One2many(
        comodel_name="membership.request.change",
        inverse_name="membership_request_id",
        string="Changes",
        domain=[("active", "=", True)],
    )
    inactive_change_ids = fields.One2many(
        comodel_name="membership.request.change",
        inverse_name="membership_request_id",
        string="Changes (Inactive)",
        domain=[("active", "=", False)],
    )

    age = fields.Integer(string="Age", compute="_compute_age", search="_search_age")

    local_voluntary = fields.Selection(
        [
            ("force_true", "Set as local voluntary"),
            ("force_false", "Not local voluntary"),
        ],
        string="Change local voluntary status",
        default=False,
        tracking=True,
    )
    regional_voluntary = fields.Selection(
        [
            ("force_true", "Set as regional voluntary"),
            ("force_false", "Not regional voluntary"),
        ],
        string="Change regional voluntary status",
        default=False,
        tracking=True,
    )
    national_voluntary = fields.Selection(
        [
            ("force_true", "Set as national voluntary"),
            ("force_false", "Not national voluntary"),
        ],
        string="Change national voluntary status",
        default=False,
        tracking=True,
    )
    local_only = fields.Selection(
        [
            ("force_true", "Set as local only"),
            ("force_false", "Not local only"),
        ],
        string="Change local only status",
        default=False,
        tracking=True,
        help="Partner wishing to be contacted only by the local",
    )

    involvement_category_ids = fields.Many2many(
        "partner.involvement.category",
        relation="membership_request_involvement_category_rel",
        column1="request_id",
        column2="category_id",
        string="Involvement Categories",
    )

    indexation_comments = fields.Text("Indexation comments")

    amount = fields.Float(digits="Product Price", copy=False)
    reference = fields.Char(copy=False)
    effective_time = fields.Datetime(copy=False, string="Involvement Date")

    nationality_id = fields.Many2one(
        comodel_name="res.country", string="Nationality", tracking=True
    )

    is_pre_processed = fields.Boolean()

    @api.model
    def _get_status_values(self, request_type, date_from=False):
        """
        :type request_type: char
        :param request_type: m or s for member or supporter.
            `False` if not defined
        :rtype: dict
        :rparam: affected date resulting of the `request_type`
            and the `status`
        """
        vals = {}
        if request_type in ["m", "s"]:
            vals["accepted_date"] = date_from or fields.Date.today()
            vals["free_member"] = request_type == "s"
        return vals

    @api.constrains("birthdate_date", "is_company", "state")
    def _check_age(self):
        required_age = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(MR_REQUIRED_AGE_KEY, default=16)
        )
        for mr in self.filtered(
            lambda s: not s.is_company
            and s.birthdate_date
            and s.request_type
            and s.state == "validate"
        ):
            if mr.age < required_age:
                raise ValidationError(
                    _("The required age for a membership request is %s") % required_age
                )

    @api.model
    def _raise_error_check_reference(self, current_id, reference, partner_id):
        """
        If the membership request contains a reference, this reference
        must be 'almost' unique:
        It can appear only on membership requests that are linked to the same partner or
        on the active membership line of the linked partner.
        We return a code error that will be interpreted in the api.constraint:
        * "exists_on_other_mr_and_no_partner_set" :
            "You didn't set a partner and the reference
            already exists on another membership request."
        * "ref_on_mr_with_other_partner" :
            "The reference already exists on a membership request
            linked to another partner."
        * "ref_on_res_partner_or_inactive_line" :
            "The reference already exists on another partner,
            or the reference corresponds to an inactive membership line."

        params:
        :current_id: the id of the membership request, 0 if not created yet
        :reference: the reference of the membership request
        :partner_id: the id of the associated partner, or False
        """

        # Compare this reference with other membership requests
        mr_with_same_ref = (
            self.env["membership.request"]
            .with_context(active_test=False)
            .search([("id", "!=", current_id), ("reference", "=", reference)])
        )
        if mr_with_same_ref and not partner_id:
            return "exists_on_other_mr_and_no_partner_set"
        elif mr_with_same_ref.filtered(
            lambda s: not s.partner_id or s.partner_id.id != partner_id
        ):
            return "ref_on_mr_with_other_partner"

        # Compare this reference with the ones on partners
        if self.env["membership.line"].search_count(
            [
                ("reference", "=", reference),
                "|",
                ("partner_id", "!=", partner_id),
                ("active", "=", False),
            ]
        ):
            return "ref_on_res_partner_or_inactive_line"
        return ""

    @api.constrains("reference")
    def _check_reference(self):
        """
        Call _raise_error_check_reference to get the error message, and raise
        the corresponding error.
        """
        for mr in self.filtered(lambda s: s.reference):
            current_id = mr.id or 0
            partner_id = mr.partner_id.id if mr.partner_id else False
            error = self._raise_error_check_reference(
                current_id, mr.reference, partner_id
            )
            if error:
                raise ValidationError(ERRORS_DICT[error])

    def _search_age(self, operator, value):
        """
        Use birthdate_date to search on age
        """
        age = value
        computed_birthdate_date = date.today() - relativedelta(years=age)
        computed_birthdate_date = datetime.strftime(
            computed_birthdate_date, DEFAULT_SERVER_DATE_FORMAT
        )
        if operator == ">=":
            operator = "<="
        elif operator == "<":
            operator = ">"
        return [("birthdate_date", operator, computed_birthdate_date)]

    def _pop_related(self, vals):
        vals.pop("local_zip", None)
        vals.pop("identifier", None)

    @api.depends("is_company", "birthdate_date")
    def _compute_age(self):
        """
        age computed depending of the birth date of the
        membership request
        """
        for mr in self:
            if not mr.is_company and mr.birthdate_date:
                mr.age = get_age(mr.birthdate_date)
            else:
                mr.age = 0

    def _get_membership_tracked_fields(self):
        """
        This method return a list of tuple defining which fields
        must create a change record.
        Tuple is structured like:
         - sequence: n° of sequence of the change, it respect the display
                     order on the screen view
         - field name: field name on view
         - request path: path to the field value from the request object
         - partner_path: path to the field value from the partner object
         - label: label to be able to ignore comparison
        """
        partner_address_path = "address_address_id"
        return [
            (1, "lastname", "lastname", "lastname", ""),
            (2, "firstname", "firstname", "firstname", ""),
            (3, "birthdate_date", "birthdate_date", "birthdate_date", ""),
            (4, "phone", "phone", "phone", ""),
            (5, "gender", "gender", "gender", ""),
            (6, "mobile", "mobile", "mobile", ""),
            (7, "email", "email", "email", ""),
            (
                8,
                "country_id",
                "country_id.display_name",
                partner_address_path + ".country_id.display_name",
                "",
            ),
            # address_local_zip_id set on request AND on partner
            (
                9,
                "city_id",
                "city_id.display_name",
                partner_address_path + ".city_id.display_name",
                "ZIP_REQUEST_PARTNER",
            ),
            # city_id set on request AND not on partner
            (
                9,
                "city_id",
                "city_id.zipcode",
                partner_address_path + ".zip_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            (
                9,
                "city_id",
                "city_id.name",
                partner_address_path + ".city_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            # city_id not set on request but on partner
            (
                9,
                "zip_man",
                "zip_man",
                partner_address_path + ".city_id.zipcode",
                "ZIP_NO_REQUEST_PARTNER",
            ),
            (
                9,
                "city_man",
                "city_man",
                partner_address_path + ".city_id.name",
                "ZIP_NO_REQUEST_PARTNER",
            ),
            # city_id not set on request and not on partner
            (
                9,
                "zip_man",
                "zip_man",
                partner_address_path + ".zip_man",
                "ZIP_NO_REQUEST_NO_PARTNER",
            ),
            (
                9,
                "city_man",
                "city_man",
                partner_address_path + ".city_man",
                "ZIP_NO_REQUEST_NO_PARTNER",
            ),
            # address_local_street_id set on request AND on partner
            (
                10,
                "address_local_street_id",
                "address_local_street_id.display_name",
                partner_address_path + ".address_local_street_id.display_name",
                "STREET_REQUEST_PARTNER",
            ),
            # address_local_street_id set on request AND not on partner
            (
                10,
                "address_local_street_id",
                "address_local_street_id.display_name",
                partner_address_path + ".street_man",
                "ZIP_REQUEST_NO_PARTNER",
            ),
            # address_local_street_id not set on request but on partner
            (
                10,
                "street_man",
                "street_man",
                partner_address_path + ".address_local_street_id.display_name",
                "STREET_NO_REQUEST_PARTNER",
            ),
            # address_local_street_id not set on request and not partner
            (
                10,
                "street_man",
                "street_man",
                partner_address_path + ".street_man",
                "STREET_NO_REQUEST_NO_PARTNER",
            ),
            (11, "number", "number", partner_address_path + ".number", "NUMBER"),
            (12, "street2", "street2", partner_address_path + ".street2", "STREET2"),
            (13, "box", "box", partner_address_path + ".box", "BOX"),
            (
                14,
                "sequence",
                "sequence",
                partner_address_path + ".sequence",
                "SEQUENCE",
            ),
            (
                15,
                "int_instance_ids",
                "expr: request.force_int_instance_id.name or "
                "request.int_instance_ids.name",
                "int_instance_ids.name",  # TODO?
                "",
            ),
            (16, "local_voluntary", "local_voluntary", "local_voluntary", "LOCAL"),
            (
                17,
                "regional_voluntary",
                "regional_voluntary",
                "regional_voluntary",
                "REGIONAL",
            ),
            (
                18,
                "national_voluntary",
                "national_voluntary",
                "national_voluntary",
                "NATIONAL",
            ),
            (19, "local_only", "local_only", "local_only", "LOCAL-ONLY"),
            (20, "nationality_id", "nationality_id.name", "nationality_id.name", ""),
        ]

    def _clean_stored_changes(self):
        chg_obj = self.env["membership.request.change"]
        chg_ids = chg_obj.search([("membership_request_id", "in", self.ids)])
        if chg_ids:
            return chg_ids.unlink()

        return False

    def _get_labels_to_process(self, request):
        label_path = [
            "LOCAL",
            "REGIONAL",
            "NATIONAL",
            "LOCAL-ONLY",
        ]
        if not request.country_id:
            return label_path
        label_path = [
            "NUMBER",
            "STREET2",
            "BOX",
            "SEQUENCE",
        ] + label_path
        partner_adr = request.partner_id.address_address_id
        if request.city_id and partner_adr.city_id:
            label_path.append("ZIP_REQUEST_PARTNER")
        elif request.city_id and not partner_adr.city_id:
            label_path.append("ZIP_REQUEST_NO_PARTNER")
        elif not request.city_id and partner_adr.city_id:
            label_path.append("ZIP_NO_REQUEST_PARTNER")
        else:
            label_path.append("ZIP_NO_REQUEST_NO_PARTNER")

        if request.address_local_street_id and partner_adr.address_local_street_id:
            label_path.append("STREET_REQUEST_PARTNER")
        elif (
            request.address_local_street_id and not partner_adr.address_local_street_id
        ):
            label_path.append("STREET_REQUEST_NO_PARTNER")
        elif (
            not request.address_local_street_id and partner_adr.address_local_street_id
        ):
            label_path.append("STREET_NO_REQUEST_PARTNER")
        else:
            label_path.append("STREET_NO_REQUEST_NO_PARTNER")
        return label_path

    def _detect_changes(self):
        tracked_fields = self._get_membership_tracked_fields()
        fields_def = self.fields_get([elem[1] for elem in tracked_fields])
        res = {}
        chg_obj = self.env["membership.request.change"]
        self._clean_stored_changes()

        for request in self:
            if not request.partner_id:
                res[request.id] = False
                continue
            label_to_process = self._get_labels_to_process(request)

            for element in tracked_fields:
                seq, field, request_path, partner_path, label = element
                if label and label not in label_to_process:
                    continue
                if request_path.startswith("expr: "):
                    request_value = safe_eval.safe_eval(
                        request_path[6:], {"request": request}
                    )
                else:
                    request_value = attrgetter(request_path)(request)
                partner_value = attrgetter(partner_path)(request.partner_id)
                field = fields_def[field]

                # If we treat voluntary fields and if request_value is False, it
                # means that the selection field is empty -> we want no change, hence
                # we set partner_value to false also.
                if not request_value and element[1] in VOLUNTARY_FIELDS:
                    partner_value = False

                if (request_value or label) and request_value != partner_value:
                    create_change = True
                    if "selection" in field:
                        selection = dict(field["selection"])
                        request_value_code = request_value
                        request_value = selection.get(request_value)
                        partner_value = selection.get(partner_value)
                        # If voluntary fields: partner field is a boolean, not selection
                        if element[1] in VOLUNTARY_FIELDS:
                            partner_value = attrgetter(partner_path)(request.partner_id)
                            if (
                                partner_value and request_value_code == "force_true"
                            ) or (
                                not partner_value
                                and request_value_code == "force_false"
                            ):
                                # In fact, there is no change since we force the actual value
                                create_change = False
                    if isinstance(request_value, bool) and isinstance(
                        partner_value, bool
                    ):
                        request_value = request_value and _("Yes") or _("No")
                        partner_value = partner_value and _("Yes") or _("No")
                    if element[1] in VOLUNTARY_FIELDS:
                        partner_value = (
                            partner_value and _("Was True") or _("Was False")
                        )
                    vals = {
                        "membership_request_id": request.id,
                        "sequence": seq,
                        "field_name": field["string"],
                        "old_value": partner_value,
                        "new_value": request_value,
                    }
                    if create_change:
                        chg_obj.create(vals)

    def _find_input_partner(self, vals):
        """
        Find, if existing, the partner to add on the membership request,
        and update lastname, firstname and email, if not given.
        - If 'mr_partner_id' is a key of _context, then take the id given in the context
        to associate the partner id and DON'T USE partner_id given in vals.
        - If 'mr_partner_id' is not in the context, use field partner_id given in vals.
        """
        # If the mr was already created (survey case), the partner may already
        # be set on the mr.
        partner = self.partner_id
        if not partner and "mr_partner_id" in self._context:
            mr_partner_id = self._context.get("mr_partner_id")
            if mr_partner_id:
                partner = self.env["res.partner"].browse(mr_partner_id)
        elif not partner and vals.get("partner_id", False):
            partner = self.env["res.partner"].browse(vals["partner_id"])

        if partner:
            if "lastname" not in vals or not vals["lastname"]:
                vals["lastname"] = partner.lastname
            if ("firstname" not in vals or not vals["firstname"]) and partner.firstname:
                vals["firstname"] = partner.firstname
            if "email" not in vals or not vals["email"]:
                vals["email"] = partner.email
        return partner

    def _find_or_create_address(self, vals):
        """
        Find address.address record if existing (based on technical name).
        Create a new address.address record if not existing.
        If no address is given (technical_name == EMPTY ADDRESS) return false.

        :rparam technical_name: the computed technical name
        :rparam address_id: the address_id, if already existing

        """
        address_local_street_id = vals.get("address_local_street_id", False)
        city_id = vals.get("city_id", False)
        number = vals.get("number", False)
        box = vals.get("box", False)
        city_man = vals.get("city_man", False)
        street_man = vals.get("street_man", False)
        zip_man = vals.get("zip_man", False)
        country_id = vals.get("country_id", False)

        technical_name = self.get_technical_name(
            address_local_street_id,
            city_id,
            number,
            box,
            city_man,
            street_man,
            zip_man,
            country_id,
        )
        if technical_name == EMPTY_ADDRESS:
            return technical_name, False
        existing_address = self.env["address.address"].search(
            [("technical_name", "=", technical_name)], limit=1
        )
        if existing_address:
            return existing_address.technical_name, existing_address.id
        else:
            address = self.env["address.address"].create(
                {
                    "country_id": country_id,
                    "street_man": street_man,
                    "zip_man": zip_man,
                    "city_man": city_man,
                    "address_local_street_id": address_local_street_id,
                    "city_id": city_id,
                    "street2": vals.get("street2", False),
                    "number": number,
                    "box": box,
                    "sequence": vals.get("sequence", False),
                }
            )
            return (
                address.technical_name,
                address.id,
            )

    @api.model
    def _manage_address_and_instance(self, vals, partner):
        """
        1. If address_id is given in vals: it is taken
        2. Elif no partner is recognized: address (complete or partial) is always taken
        3. Else, if
          A. Partner has no address at all -> partial or complete address is always taken
          B. Partner has an address -> it can be modified only by a
            complete (with street) address

        The instance is taken on the address if and only if the address from the MR is taken
        """
        values = {}
        mr_address_id = vals.get("address_id", False)
        if mr_address_id:
            # 1.
            address = self.env["address.address"].browse(mr_address_id)
            values["address_id"] = mr_address_id
            values["technical_name"] = (
                self.env["address.address"].browse(mr_address_id).technical_name
            )

        else:
            technical_name, address_id = self._find_or_create_address(vals)
            address = (
                self.env["address.address"].browse(address_id) if address_id else False
            )
            values["technical_name"] = technical_name
            if not partner:
                # 2.
                values["address_id"] = address_id

            else:
                # 3.
                if not partner.address_address_id:
                    values["address_id"] = address_id
                else:
                    if address and address.has_street:
                        values["address_id"] = address_id

        # Manage instances
        if values.get("address_id", False):
            int_instance_id = self.get_int_instance_id(address.city_id.id)
            values["int_instance_ids"] = [(4, int_instance_id)]
        elif vals.get("int_instance_ids", False):
            # If no address but an instance is given, take it
            values["int_instance_ids"] = vals.get("int_instance_ids")

        # Force instance must also be taken
        values["force_int_instance_id"] = vals.get("force_int_instance_id", False)

        return values

    @api.model
    def _pre_process(self, input_vals):  # noqa: C901
        """
        Try:
        ** to find a zipcode and a country
        ** to build a birthdate_date
        ** to find an existing partner

        :rparam output_vals: input values dictionary ready
                      to create a ``membership_request``, built from input_vals input dict
        """
        partner = self._find_input_partner(input_vals)
        partner_id = partner.id if partner else False
        output_vals = {}
        if "lastname" not in input_vals or not input_vals["lastname"]:
            # No lastname -> not an interesting request, we do nothing
            return input_vals

        for key in ["lastname", "firstname"]:
            val = input_vals.get(key, False)
            if val:
                input_vals[key] = val.strip().title()
        is_company = input_vals.get("is_company", False)
        lastname = input_vals.get("lastname", False)
        firstname = False if is_company else input_vals.get("firstname", False)
        request_type = input_vals.get("request_type", False)
        email = input_vals.get("email", False)
        phone = input_vals.get("phone", False)
        mobile = input_vals.get("mobile", False)
        birthdate_date = (
            False if is_company else input_vals.get("birthdate_date", False)
        )
        day = False if is_company else input_vals.get("day", False)
        month = False if is_company else input_vals.get("month", False)
        year = False if is_company else input_vals.get("year", False)
        # It may happen that birthdate_date is given, but not day, month and year (coming from a
        # survey for example). In this case fill the fields.
        if birthdate_date and isinstance(birthdate_date, date):
            day = birthdate_date.day
            month = birthdate_date.month
            year = birthdate_date.year

        gender = False if is_company else input_vals.get("gender", False)

        address_id = input_vals.get("address_id", False)
        city_id = input_vals.get("city_id", False)
        city_man = input_vals.get("city_man", False)
        country_id = input_vals.get("country_id", False)
        zip_man = input_vals.get("zip_man", False)

        candidate_city = False
        if not city_id and zip_man and city_man:
            domain = [
                ("zipcode", "=", zip_man),
                ("name", "ilike", city_man),
            ]
            candidate_city = self.env["res.city"].search(domain, limit=1)
        elif city_man and not city_id:
            domain = [
                ("name", "ilike", city_man),
            ]
            candidate_city = self.env["res.city"].search(domain, limit=2)
            if len(candidate_city) != 1:
                # Take the city only if it is unique
                candidate_city = False
        if (
            not candidate_city
            and not city_id
            and zip_man
            and not city_man
            and not country_id
        ):
            domain = [
                ("zipcode", "=", zip_man),
            ]
            candidate_city = self.env["res.city"].search(domain, limit=1)
        if candidate_city or city_id:
            be_country_id = self.env["res.country"]._country_default_get("BE").id
            if not country_id or be_country_id == country_id:
                # Default country is BE.
                # In this case city_man and zip_man are reset to False
                country_id = be_country_id
                city_id = city_id or candidate_city.id
                city_man = False
                zip_man = False

        # If city_id but no country, we now have to force the country
        if city_id and not country_id:
            country_id = self.env["res.city"].browse(city_id).country_id.id

        if not is_company and not birthdate_date:
            birthdate_date = self.get_birthdate_date(day, month, year)
        if mobile:
            mobile = self.get_format_phone_number(mobile)
        if phone:
            phone = self.get_format_phone_number(phone)
        if email:
            email = self.get_format_email(email)

        # Try to recognize the partner, if not given in input_vals
        if not partner:
            recognizable_values = {
                "is_company": is_company,
                "birthdate_date": birthdate_date,
                "lastname": lastname,
                "firstname": firstname,
                "email": email,
                "mobile": mobile,
                "phone": phone,
            }
            partner = self.get_partner_id(recognizable_values)
            if partner:
                partner_id = partner.id

        output_vals.update(
            {
                "is_company": is_company,
                "partner_id": partner_id,
                "lastname": lastname,
                "firstname": firstname,
                "request_type": request_type,
                "birthdate_date": birthdate_date,
                "day": day,
                "month": month,
                "year": year,
                "gender": gender,
                "mobile": mobile,
                "phone": phone,
                "email": email,
                "address_id": address_id,
                "city_id": city_id,
                "country_id": country_id,
                "zip_man": zip_man,
                "city_man": city_man,
            }
        )
        # We now check all other keys from input_vals:
        # if the key is not in output_vals and if it corresponds
        # to a field from membership.request, we add it to output_vals
        # It is useful to copy all other address fields.
        for key in input_vals.keys():
            if (
                key not in output_vals
                and key in self.env["membership.request"].fields_get()
            ):
                output_vals[key] = input_vals[key]

        # Manage address and instances.
        output_vals.update(self._manage_address_and_instance(output_vals, partner))

        res = self._onchange_partner_id_vals(
            is_company, request_type, partner_id, output_vals["technical_name"]
        )
        # Do not manage int_instance_ids separately from address in pre-process
        res.pop("int_instance_ids", False)
        output_vals.update(res)

        # Finally manage int_instance: if partner is recognized and no int_instance is set
        # (due to an address modification), take the partner's instance as a reminder on the MR.
        if not output_vals.get("int_instance_ids", False) and partner:
            output_vals["int_instance_ids"] = [(6, 0, partner.int_instance_ids.ids)]

        output_vals["state"] = "confirm"
        output_vals["is_pre_processed"] = True
        return output_vals

    @api.onchange("country_id")
    def onchange_country_id(self):
        self_sudo = self.sudo()
        for req in self_sudo:
            vals = {
                "city_id": False,
                "technical_name": self_sudo.get_technical_name(
                    False,
                    False,
                    self.number,
                    self.box,
                    self.city_man,
                    self.street_man,
                    self.zip_man,
                    self.country_id.id,
                ),
                "int_instance_ids": [(6, 0, [self.get_int_instance_id(False)])],
            }
            req.update(vals)

    @api.onchange("city_id")
    def onchange_city_id(self):
        self_sudo = self.sudo()
        for req in self_sudo:
            vals = {
                "address_local_street_id": False,
                "technical_name": self_sudo.get_technical_name(
                    False,
                    self_sudo.city_id.id,
                    self_sudo.number,
                    self_sudo.box,
                    self_sudo.city_man,
                    self_sudo.street_man,
                    self_sudo.zip_man,
                    self_sudo.country_id.id,
                ),
                "local_zip": self_sudo.city_id.zipcode,
                "int_instance_ids": [
                    (6, 0, [self.get_int_instance_id(self_sudo.city_id.id)])
                ],
            }
            req.update(vals)

    # view methods: onchange, button

    @api.onchange(
        "zip_man", "city_man", "address_local_street_id", "street_man", "number", "box"
    )
    def onchange_other_address_componants(self):
        for req in self.sudo():
            req.technical_name = req.get_technical_name(
                req.address_local_street_id.id,
                req.city_id.id,
                req.number,
                req.box,
                req.city_man,
                req.street_man,
                req.zip_man,
                req.country_id.id,
            )

    @api.onchange("technical_name")
    def onchange_technical_name(self):
        for req in self.sudo():
            address_ids = (
                self.env["address.address"]
                .sudo()
                .search([("technical_name", "=", req.technical_name)], limit=1)
            )
            req.address_id = address_ids

    @api.onchange(
        "lastname", "firstname", "day", "month", "year", "email", "phone", "mobile"
    )
    def onchange_partner_component(self):
        """
        try to find a new partner_id depending of the
        birthdate_date, lastname, firstname, email, mobile, phone
        """
        for req in self.sudo():
            birthdate_date = False
            if not req.is_company:
                birthdate_date = self.get_birthdate_date(req.day, req.month, req.year)
            email = self.get_format_email(req.email)

            req.birthdate_date = "%s" % birthdate_date if birthdate_date else False
            req.email = email
            if req.is_update:
                continue

            recognizable_values = {
                "is_company": req.is_company,
                "birthdate_date": birthdate_date,
                "lastname": req.lastname,
                "firstname": req.firstname,
                "email": email,
                "mobile": req.mobile,
                "phone": req.phone,
            }

            partner_id = self.get_partner_id(recognizable_values)

            req.partner_id = partner_id

    @api.onchange("partner_id", "request_type", "is_company")
    def onchange_partner_id(self):
        """
        Take current
            * membership_state_id
            * interest_ids
            * competency_ids
            * voluntaries
        of ``partner_id``
        And set corresponding fields into the ``membership.request``

        **Note**
        fields are similarly named
        """
        self.env["membership.request"].sudo()
        for req in self:
            req.update(
                req._onchange_partner_id_vals_multi(
                    req.is_company,
                    req.request_type,
                    req.partner_id.id,
                    req.technical_name,
                )
            )

    def _onchange_partner_id_vals_multi(
        self, is_company, request_type, partner_id, technical_name
    ):
        # for inherit
        self.ensure_one()
        return self._onchange_partner_id_vals(
            is_company, request_type, partner_id, technical_name
        )

    @api.model
    def _onchange_partner_id_vals(
        self, is_company, request_type, partner_id, technical_name
    ):
        """
        Take current
            * membership_state_id
            * interest_ids
            * competency_ids
        of ``partner_id``
        And set corresponding fields into the ``membership.request``

        **Note**
        fields are similarly named
        """
        res = {
            "interest_ids": False,
            "competency_ids": False,
            "identifier": False,
        }
        def_status_id = self.env["membership.state"]._get_default_state()
        partner_status_id = False
        membership_state_code = False
        if partner_id:
            partner = self.env["res.partner"].sudo().browse(partner_id)
            # take current status of partner
            partner_status_id = (
                partner.membership_state_id and partner.membership_state_id.id or False
            )
            membership_state_code = partner.membership_state_code
            interests_ids = [term.id for term in partner.interest_ids]
            res["interest_ids"] = interests_ids and [[6, False, interests_ids]] or False
            competency_ids = [trm.id for trm in partner.competency_ids]
            res["competency_ids"] = (
                competency_ids and [[6, False, competency_ids]] or False
            )
            res["identifier"] = partner.identifier

            if technical_name == EMPTY_ADDRESS:
                res["int_instance_ids"] = partner.int_instance_ids.ids

        elif not is_company:
            partner_status_id = def_status_id.id

        result_type = self.env["membership.state"]
        if not is_company:
            result_type = self.get_partner_preview(request_type, partner_id)
        else:
            res.update(
                {
                    "request_type": False,
                }
            )
        if result_type.code in [
            False,
            "without_membership",
            "supporter",
            "former_supporter",
        ]:
            res.update(
                {
                    "local_voluntary": False,
                    "regional_voluntary": False,
                    "national_voluntary": False,
                }
            )
        elif any(
            [
                result_type.code == "member_candidate"
                and membership_state_code in [False, "without_membership", "supporter"],
                result_type.code == "member_committee"
                and membership_state_code == "supporter",
            ]
        ):
            res.update(
                {
                    "local_voluntary": "force_true",
                    "regional_voluntary": "force_true",
                    "national_voluntary": "force_true",
                }
            )
        if result_type.code in [
            "supporter",
            "former_supporter",
            "member_candidate",
            "member_committee",
            "member",
            "former_member",
            "former_member_committee",
        ]:
            res["local_only"] = "force_false"

        res.update(
            {
                "membership_state_id": partner_status_id,
                "result_type_id": result_type.id if result_type else False,
            }
        )
        return res

    @api.onchange("mobile")
    def onchange_mobile(self):
        for req in self:
            req.mobile = self.get_format_phone_number(req.mobile)

    @api.onchange("phone")
    def onchange_phone(self):
        for req in self:
            req.phone = self.get_format_phone_number(req.phone)

    # public method
    @api.model
    def get_partner_preview(self, request_type, partner_id=False):
        """
        Advance partner's workflow to catch the next state
        If no partner then create one
        See also write and create method in abstract_model, it is important
        that disable_tracking remains always True during the entire simulation
        :type request_type: char
        :param request_type: m or s (member or supporter)
        :type partner_id: res.partner
        :param partner_id: partner
        :rparam: next status in partner's workflow depending on `request_type`
        """
        self_context = self.with_context(tracking_disable=True)

        partner_obj = self_context.env["res.partner"]
        status_obj = self.env["membership.state"]
        self.env.ref("mozaik_membership.former_member")
        name = '"preview-%s"' % uuid4().hex
        self.flush()
        self.env.cr.execute("SAVEPOINT %(savepoint)s", {"savepoint": AsIs(name)})
        try:
            if partner_id:
                partner = partner_obj.browse(partner_id)
            else:
                partner_datas = {
                    "lastname": "%s" % uuid4(),
                    "identifier": "-1",
                }
                partner = partner_obj.create(partner_datas)
            # didn't find a good way to make it in the statechart
            # # pylint: disable=assignment-from-none
            event = self._get_event_get_partner_preview(partner, request_type)
            vals = self._get_status_values(request_type)
            if vals:
                partner.sudo().write(vals)
            state_code = partner.sudo().simulate_next_state(event)
            partner.flush()
            partner.invalidate_cache(ids=partner.ids)
        finally:
            self.env.cr.execute(
                "ROLLBACK TO SAVEPOINT %(savepoint)s", {"savepoint": AsIs(name)}
            )
        return status_obj.search([("code", "=", state_code)], limit=1)

    def _get_event_get_partner_preview(self, partner, request_type):
        return None

    def get_birthdate_date(self, day, month, year):
        """
        ==============
        get_birthdate_date
        ==============
        Return a birth date case where all parameters day/month/year
        are initialized
        """
        birthdate_date = False
        if day and month and year:
            try:
                birthdate_date = date(int(year), int(month), int(day)).strftime(
                    "%Y-%m-%d"
                )
            except Exception:
                _logger.info("Reset `birthdate_date`: Invalid Date")
        return birthdate_date

    def _get_partner_domains(self, recognizable_values):
        partner_domains = []

        is_company = recognizable_values.get("is_company", False)
        birthdate_date = recognizable_values.get("birthdate_date", False)
        lastname = recognizable_values.get("lastname", False)
        firstname = recognizable_values.get("firstname", False)
        email = recognizable_values.get("email", False)

        if not is_company and birthdate_date and email and firstname and lastname:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birthdate_date','=', '%s'),"
                "('email', '=ilike', '%s'),"
                "('firstname', '=ilike', \"%s\"),"
                "('lastname', '=ilike', \"%s\")]"
                % (birthdate_date, email, firstname, lastname)
            )
        if not is_company and birthdate_date and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birthdate_date','=', '%s'),"
                "('email', '=ilike', '%s')]" % (birthdate_date, email)
            )
        if not is_company and email and firstname and lastname:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('email', '=ilike', '%s'),"
                "('firstname', '=ilike', \"%s\"),"
                "('lastname', '=ilike', \"%s\")]" % (email, firstname, lastname)
            )
        if not is_company and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('email', '=ilike','%s')]" % (email)
            )
        if is_company and email:
            partner_domains.append(
                "[('is_company', '=', True)," "('email', '=ilike','%s')]" % (email)
            )
        if lastname:
            if not is_company and firstname:
                partner_domains.append(
                    "[('membership_state_id','!=',False),"
                    "('is_company', '=', False),"
                    "('firstname', '=ilike', \"%s\"),"
                    "('lastname', '=ilike', \"%s\")]" % (firstname, lastname)
                )
            elif not is_company:
                partner_domains.append(
                    "[('membership_state_id', '!=', False),"
                    "('is_company', '=', False),"
                    "('lastname', '=ilike', \"%s\")]" % (lastname)
                )
            else:
                partner_domains.append(
                    "[('is_company', '=', True),"
                    "('lastname', '=ilike', \"%s\")]" % (lastname)
                )
        return partner_domains

    def get_partner_id(self, recognizable_values):
        """
        Make special combinations of domains to try to find
        a unique partner_id
        """
        partner_domains = self._get_partner_domains(recognizable_values)
        for domain in partner_domains:
            try:
                safe_domain = safe_eval.safe_eval(domain)
            except Exception as e:
                raise ValidationError(_("Invalid Data")) from e
            res_ids = self.env["res.partner"].search(safe_domain)
            if len(res_ids) == 1:
                return res_ids

        return False

    def get_technical_name(
        self,
        address_local_street_id,
        city_id,
        number,
        box,
        city_man,
        street_man,
        zip_man,
        country_id,
    ):
        if not country_id:
            return EMPTY_ADDRESS
        if city_id:
            zip_man, city_man = False, False
        values = OrderedDict(
            [
                ("country_id", country_id),
                ("city_id", city_id),
                ("zip_man", zip_man),
                ("city_man", city_man),
                ("address_local_street_id", address_local_street_id),
                ("street_man", street_man),
                ("number", number),
                ("box", box),
            ]
        )
        address_obj = self.env["address.address"]
        technical_name = address_obj._get_technical_name(values)
        return technical_name

    def get_format_email(self, email):
        """
        ``Check and format`` email just like `email.coordinate` make it
        :rparam: formated email value
        """
        if email:
            if check_email(email):
                email = format_email(email)
        return email

    def get_format_phone_number(self, number):
        """
        Format a phone number with the same way as phone.phone do it.
        Call with a special context to avoid exception
        """
        if number:
            try:
                number = check_and_format_number(
                    number,
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("default.country.code", default="BE"),
                )
            except UserError:
                _logger.info("Unable to format phone number %s", number)

        return number

    def confirm_request(self):
        vals = {"state": "confirm"}
        # superuser_id because of record rules
        return self.sudo().write(vals)

    def validate_request(self):  # noqa: C901
        """
        First check if the relations are set. For those try to update
        content
        In Other cases then create missing required data
        """
        mr_vals = {}
        for mr in self:
            partner_values = {
                "is_company": mr.is_company,
                "lastname": mr.lastname,
            }
            partner_add_values(mr, partner_values)

            new_interests_ids = []
            if not mr.is_company:
                new_interests_ids = (
                    mr.interest_ids
                    and ([interest.id for interest in mr.interest_ids])
                    or []
                )
            new_competency_ids = (
                mr.competency_ids
                and ([competence.id for competence in mr.competency_ids])
                or []
            )

            notes = []
            if mr.note:
                notes.append(mr.note)
            if mr.partner_id and mr.partner_id.comment:
                notes.append(mr.partner_id.comment)

            indexation_comments = []
            if mr.indexation_comments:
                indexation_comments.append(mr.indexation_comments)
            if mr.partner_id and mr.partner_id.indexation_comments:
                indexation_comments.append(mr.partner_id.indexation_comments)

            partner_values.update(
                {
                    "competency_ids": [[6, False, new_competency_ids]],
                    "interest_ids": [[6, False, new_interests_ids]],
                    "comment": notes and "\n".join(notes) or False,
                    "indexation_comments": indexation_comments
                    and "\n".join(indexation_comments)
                    or False,
                }
            )

            partner = mr.partner_id
            if not mr.partner_id:
                mr._get_instance_partner(partner_values)
                partner = self.env["res.partner"].create(partner_values)
                mr_vals["partner_id"] = partner.id
                partner_values = {}
            else:
                # Do not update firstname and lastname if the only modifications
                # are upper/lower case changes
                if (
                    partner.lastname
                    and mr.lastname
                    and partner.lastname.lower() == mr.lastname.lower()
                ):
                    partner_values.pop("lastname", False)
                if (
                    partner.firstname
                    and mr.firstname
                    and partner.firstname.lower() == mr.firstname.lower()
                ):
                    partner_values.pop("firstname", False)

            # create new involvements
            self._validate_request_involvement(mr, partner)

            self._validate_voluntaries(mr, partner)

            self._validate_request_coordinates(mr, partner_values)

            # Before changing the membership, compute if address must be changed.
            # If not, erase int_instance_ids, otherwise it will change the instance (without
            # changing the address, which is unwanted).

            address_vals = {
                "address_local_street_id": mr.address_local_street_id.id,
                "city_id": mr.city_id.id,
                "number": mr.number,
                "box": mr.box,
                "city_man": mr.city_man,
                "street_man": mr.street_man,
                "zip_man": mr.zip_man,
                "country_id": mr.country_id.id,
            }
            res_values = self._manage_address_and_instance(address_vals, partner)
            old_technical_name = mr.is_pre_processed and mr.address_id.technical_name
            new_technical_name = res_values.get("technical_name", False)
            if not mr.is_pre_processed or old_technical_name != new_technical_name:
                mr.address_id = res_values.get("address_id", False)
                mr.technical_name = res_values["technical_name"]
            if not mr.address_id:
                mr.int_instance_ids = [(6, 0, partner.int_instance_ids.ids)]

            mr._validate_request_membership_with_checks(partner)

            if (
                mr.result_type_id.code == "without_membership"
                and mr.force_int_instance_id
            ):
                # If partner is without_membership, no membership line exists on it,
                # hence the force instance will not be modified inside
                # _validate_request_membership, we must do it explicitly
                partner_values["force_int_instance_id"] = mr.force_int_instance_id

            if mr.address_id:
                # Write the address on the partner, and change the instance.
                # Only case where the instance must NOT be changed:
                # force instance is set
                update_instance = not bool(mr.force_int_instance_id)
                mr._partner_write_address(mr.address_id, partner, update_instance)

            if partner_values:
                partner.write(partner_values)

        # if request `validate` then object should be invalidated
        mr_vals.update({"state": "validate"})

        # superuser_id because of record rules
        self.sudo().action_invalidate(vals=mr_vals)
        return True

    def _partner_write_address(self, address_id, partner, update_instance):
        """
        Write the address on the partner, only if it is a different one (otherwise trigger
        unwanted logic, assuming that the address REALLY changes).
        Use change address wizard.
        It can happen that the address isn't linked to an instance
        (if the address has no city_id). In this case don't update instance.

        Intended to be extended.
        """
        if partner and (
            not partner.address_address_id or partner.address_address_id != address_id
        ):
            wiz = self.env["change.address"].create(
                {
                    "address_id": address_id.id,
                    "partner_ids": [(4, partner.id)],
                    "update_instance": update_instance if address_id.city_id else False,
                }
            )
            wiz.doit()

    def _validate_request_membership_with_checks(self, partner):
        self.ensure_one()
        active_lines = partner.membership_line_ids.filtered(lambda m: m.active)
        if (
            self.result_type_id != self.membership_state_id
            or (
                self.force_int_instance_id
                and self.force_int_instance_id != partner.int_instance_ids
            )
            or (
                self.int_instance_ids
                and self.int_instance_ids != partner.int_instance_ids
            )
            or (active_lines and active_lines[0].price != self.amount)
        ):
            self._validate_request_membership(partner)

    def _validate_request_membership(self, partner):
        self.ensure_one()
        active_memberships = partner.membership_line_ids.filtered(lambda s: s.active)
        if self.force_int_instance_id:
            # we want only one instance
            active_memberships.filtered(
                lambda s, i=self.force_int_instance_id: s.int_instance_id != i
            )._close(force=True)

        for instance in self.force_int_instance_id or self.int_instance_ids:
            membership_instance = active_memberships.filtered(
                lambda s, i=instance: s.int_instance_id == i
            )
            update_amount_membership_line = self.env["membership.line"].browse()
            if self.result_type_id.code != "without_membership" and (
                not membership_instance
                or membership_instance.state_id != self.result_type_id
            ):
                if active_memberships:
                    active_memberships._close(force=True)
                    active_memberships.flush()
                    vals = {
                        "int_instance_id": instance.id,
                        "partner_id": partner.id,
                        "product_id": membership_instance.product_id.id
                        or partner.subscription_product_id.id,
                        "state_id": self.result_type_id.id,
                    }
                    if active_memberships.paid:
                        vals["price"] = 0
                    w = self.env["add.membership"].create(vals)
                    if (
                        not active_memberships.paid
                        or active_memberships.state_id.free_state
                    ):
                        # If we were in a free state, it is marked as paid by default, but
                        # the next paid membership must not be marked as paid (without
                        # registering a payment).
                        w._onchange_product_id()  # compute the price
                else:
                    w = self.env["add.membership"].create(
                        {
                            "int_instance_id": instance.id,
                            "partner_id": partner.id,
                            "product_id": partner.subscription_product_id.id,
                            "state_id": self.result_type_id.id,
                        }
                    )
                    w._onchange_product_id()  # compute the price
                update_amount_membership_line = w.action_add()

            elif self.result_type_id.code in ("member", "member_candidate"):
                update_amount_membership_line = partner.membership_line_ids.filtered(
                    lambda m, i=instance: m.int_instance_id == i
                    and m.active
                    and not m.paid
                )

            # save membership amount
            if self.amount > 0.0 or self.reference:
                product = self.env["product.product"].search(
                    [
                        ("membership", "=", True),
                        ("list_price", "=", self.amount),
                    ],
                    limit=1,
                )
                vals = {}
                if self.reference:
                    vals["reference"] = self.reference
                if self.amount:
                    vals["price"] = self.amount
                if product:
                    vals["product_id"] = product.id
                for membership in update_amount_membership_line:
                    body = (
                        _("Membership changed with membership request:")
                        + "<br/><ul class='o_Message_trackingValues'>"
                    )
                    arrow = "<div class='fa fa-long-arrow-right'></div>"
                    if self.reference:
                        body += _(
                            "<li>Reference: %(previous)s %(arrow)s %(after)s</li>"
                        ) % {
                            "previous": membership.reference,
                            "arrow": arrow,
                            "after": self.reference,
                        }
                    if self.amount:
                        body += _(
                            "<li>Price: %(previous)s %(arrow)s %(after)s</li>"
                        ) % {
                            "previous": membership.price,
                            "arrow": arrow,
                            "after": self.amount,
                        }
                    if product:
                        body += _(
                            "<li>Product: %(previous)s %(arrow)s %(after)s</li>"
                        ) % {
                            "previous": membership.product_id.name,
                            "arrow": arrow,
                            "after": product.name,
                        }
                    membership.partner_id.message_post(body=body)
                update_amount_membership_line.write(vals)

    @api.model
    def _validate_voluntaries(self, mr, partner):
        """
        We consider selection fields
        * local_voluntary
        * regional_voluntary
        * national_voluntary
        * local_only
        on membership request, and if a value is forced, we write it
        on the partner
        """
        if not partner:
            return
        if mr.local_voluntary == "force_true":
            partner.local_voluntary = True
        elif mr.local_voluntary == "force_false":
            partner.local_voluntary = False
        if mr.regional_voluntary == "force_true":
            partner.regional_voluntary = True
        elif mr.regional_voluntary == "force_false":
            partner.regional_voluntary = False
        if mr.national_voluntary == "force_true":
            partner.national_voluntary = True
        elif mr.national_voluntary == "force_false":
            partner.national_voluntary = False
        if mr.local_only == "force_true":
            partner.local_only = True
        elif mr.local_only == "force_false":
            partner.local_only = False

    @api.model
    def _validate_request_involvement(self, mr, partner):
        current_categories = partner.partner_involvement_ids.mapped(
            "involvement_category_id"
        )
        new_categories = mr.involvement_category_ids.filtered(
            lambda s, cc=current_categories: s not in cc or s.allow_multi
        )
        for ic in new_categories:
            vals = {
                "partner_id": partner.id,
                "effective_time": mr.effective_time,
                "involvement_category_id": ic.id,
            }
            if ic.involvement_type == "donation":
                vals.update(
                    {
                        "reference": mr.reference,
                        "amount": mr.amount,
                    }
                )
            self.env["partner.involvement"].create(vals)

    @api.model
    def _validate_request_coordinates(self, mr, partner_values):
        # case of email: do not change email if only difference is lower/upper case
        if mr.email and (
            not mr.partner_id.email or mr.email.lower() != mr.partner_id.email.lower()
        ):
            partner_values["email"] = mr.email
        # case of phone
        if mr.phone:
            partner_values["phone"] = mr.phone
        # case of mobile
        if mr.mobile:
            partner_values["mobile"] = mr.mobile

    def cancel_request(self):
        # superuser_id because of record rules
        self.sudo().action_invalidate(vals={"state": "cancel"})
        return True

    def _get_instance_partner(self, partner_values):
        """
        If the membership request concerns a new partner and if an internal instance
        is present on the membership request, we use it to force the instance
        of the partner.
        """
        self.ensure_one()
        if not self.partner_id and self.force_int_instance_id:
            partner_values.update(
                {"force_int_instance_id": self.force_int_instance_id.id}
            )
        elif not self.partner_id and self.int_instance_ids:
            partner_values.update({"force_int_instance_id": self.int_instance_ids.id})

    @api.model
    def get_int_instance_id(self, city_id):
        """
        :rtype: integer
        :rparam: instance id of address local zip or default instance id if
            `address_local_zip_id` is False
        """
        if city_id:
            zip_obj = self.env["res.city"]
            zip_rec = zip_obj.browse(city_id)
            return zip_rec.int_instance_id.id
        else:
            return first(self.env.user.partner_id.int_instance_m2m_ids).id

    @api.model_create_single
    def create(self, vals):
        # Automatically correct case errors in firstname and lastname
        # Will not be corrected in write() so user can bypass
        # this modification.
        for key in ["lastname", "firstname"]:
            val = vals.get(key, False)
            if val:
                vals[key] = val.strip().title()
        if (
            self.env.context.get("install_mode", False)
            or self.env.context.get("mode", True) == "pre_process"
        ):
            vals = self._pre_process(vals)

        # do not pass related fields to the orm
        self._pop_related(vals)
        if "day" in vals and "month" in vals and "year" in vals:
            vals["birthdate_date"] = self.get_birthdate_date(
                vals.get("day"), vals.get("month"), vals.get("year")
            )
        request_id = super().create(vals)
        request_id._detect_changes()

        return request_id

    def write(self, vals):
        # If reference is not in vals but partner_id is, trigger _check_reference after write
        check_ref = "partner_id" in vals and "reference" not in vals
        # do not pass related fields to the orm
        active_ids = self.search([("id", "in", self.ids), ("active", "=", True)])
        self._pop_related(vals)
        # we need to recompute the day since it's readonly
        if "day" in vals or "month" in vals or "year" in vals:
            for req in self:
                vals["birthdate_date"] = self.get_birthdate_date(
                    vals.get("day", req.day),
                    vals.get("month", req.month),
                    vals.get("year", req.year),
                )
        res = super().write(vals)
        if check_ref:
            self.filtered(lambda mr: mr.state != "validate")._check_reference()
        if "active" in vals:
            if not vals.get("active"):
                active_ids = []
        if active_ids:
            active_ids._detect_changes()
        return res

    def name_get(self):
        """
        display name is `lastname firstname`
        **Note**
        if firstname is empty then it is just lastname alone
        """
        res = []
        for record in self:
            display_name = (
                "%s" % record.lastname
                if not record.firstname
                else "%s %s" % (record.lastname, record.firstname)
            )
            res.append((record["id"], display_name))
        return res
